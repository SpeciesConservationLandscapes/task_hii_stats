import argparse
import ee
from task_base import HIITask, PROJECTS


class HIIStats(HIITask):
    inputs = {
        "hii": {
            "ee_type": HIITask.IMAGECOLLECTION,
            "ee_path": f"{PROJECTS}/HII/v1/hii",
            "maxage": 1,
        },
        "states": {
            "ee_type": HIITask.FEATURECOLLECTION,
            "ee_path": f"{PROJECTS}/SCL/v1/source/gadm404_state_simp",
            "static": True,  # TODO: make dynamic
        },
    }

    def _get_stat(self, val):
        return ee.Number(
            ee.Algorithms.If(val, ee.Number(val).round().divide(100), None)
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hii, _ = self.get_most_recent_image(
            ee.ImageCollection(self.inputs["hii"]["ee_path"])
        )
        self.area = ee.Image.pixelArea().divide(1000000)
        self.stats_reducer = (
            ee.Reducer.mean()
            .combine(ee.Reducer.min(), None, True)
            .combine(ee.Reducer.max(), None, True)
            .combine(ee.Reducer.stdDev(), None, True)
            .combine(ee.Reducer.sum(), None, True)
        )
        self.states = ee.FeatureCollection(self.inputs["states"]["ee_path"])

    def calc(self):
        hiidate_stats_image = self.hii.addBands(self.area)

        def get_feature_stats(feature):
            stats = hiidate_stats_image.reduceRegion(
                reducer=self.stats_reducer,
                geometry=feature.geometry(),
                crs=self.hii.projection(),
                scale=self.hii.projection().nominalScale(),
                maxPixels=1e15,
            )

            hii_sum = ee.Number(stats.get("hii_sum"))
            area_sum = ee.Number(stats.get("area_sum"))
            normalized_hii_area = ee.Number(
                ee.Algorithms.If(hii_sum, hii_sum.divide(area_sum), None)
            )

            results = ee.Dictionary(
                {
                    "mean": self._get_stat(stats.get("hii_mean")),
                    "min": self._get_stat(stats.get("hii_min")),
                    "max": self._get_stat(stats.get("hii_max")),
                    "std_dev": self._get_stat(stats.get("hii_stdDev")),
                    "sum_per_area": self._get_stat(normalized_hii_area),
                }
            )

            return feature.set("stats", results)

        # Global stats
        global_poly = ee.Geometry.Polygon(
            coords=self.aoi[0], proj=self.crs, geodesic=False
        )
        global_stats = get_feature_stats(ee.Feature(global_poly, {}))
        global_stats_fc = ee.FeatureCollection(global_stats)
        global_stats_path = (
            f"{self.taskdate.isoformat()}/hii_stats_global_{self.taskdate.isoformat()}"
        )
        self.table2storage(global_stats_fc, "hii-stats", global_stats_path)

        # Stats per country
        country_stats = self.countries.map(get_feature_stats)
        country_stats_path = (
            f"{self.taskdate.isoformat()}/hii_stats_country_{self.taskdate.isoformat()}"
        )
        self.table2storage(country_stats, "hii-stats", country_stats_path)

        # Stats per state/province
        # state_stats = self.states.map(get_feature_stats)
        # state_stats_path = (
        #     f"{self.taskdate.isoformat()}/hii_stats_state_{self.taskdate.isoformat()}"
        # )
        # self.table2storage(state_stats, "hii-stats", state_stats_path)

    def check_inputs(self):
        super().check_inputs()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--taskdate")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="overwrite existing outputs instead of incrementing",
    )
    options = parser.parse_args()
    weightedsum_task = HIIStats(**vars(options))
    weightedsum_task.run()
