from tests.integration.base import DBTIntegrationTest, use_profile


class TestIncrementalOnSchemaChange(DBTIntegrationTest):
    @property
    def models(self):
        return "models"

    @property
    def project_config(self):
        return {"config-version": 2, "test-paths": ["tests"]}

    def run_twice_and_assert(self, include, compare_source, compare_target):
        # dbt run (twice)
        run_args = ["run"]
        if include:
            run_args.extend(("--models", include))
        results_one = self.run_dbt(run_args)
        results_two = self.run_dbt(run_args)

        self.assertEqual(len(results_one), 3)
        self.assertEqual(len(results_two), 3)

        self.assertTablesEqual(compare_source, compare_target)

    def run_incremental_ignore(self):
        select = "model_a incremental_ignore incremental_ignore_target"
        compare_source = "incremental_ignore"
        compare_target = "incremental_ignore_target"
        self.run_twice_and_assert(select, compare_source, compare_target)

    def run_incremental_append_new_columns(self):
        select = "model_a incremental_append_new_columns incremental_append_new_columns_target"
        compare_source = "incremental_append_new_columns"
        compare_target = "incremental_append_new_columns_target"
        self.run_twice_and_assert(select, compare_source, compare_target)

    def run_incremental_fail_on_schema_change(self):
        select = "model_a incremental_fail"
        results_one = self.run_dbt(["run", "--models", select, "--full-refresh"])  # noqa: F841
        results_two = self.run_dbt(["run", "--models", select], expect_pass=False)
        self.assertIn("Compilation Error", results_two[1].message)

    def run_incremental_sync_all_columns(self):
        # this doesn't work on Delta today
        select = "model_a incremental_sync_all_columns incremental_sync_all_columns_target"
        results_one = self.run_dbt(["run", "--models", select, "--full-refresh"])  # noqa: F841
        results_two = self.run_dbt(["run", "--models", select], expect_pass=False)
        self.assertIn("Compilation Error", results_two[1].message)


class TestDeltaAppend(TestIncrementalOnSchemaChange):
    @property
    def project_config(self):
        return {
            "config-version": 2,
            "test-paths": ["tests"],
            "models": {
                "+incremental_strategy": "append",
            },
        }

    @use_profile("databricks_cluster")
    def test__databricks_cluster__run_incremental_ignore(self):
        self.run_incremental_ignore()

    @use_profile("databricks_cluster")
    def test__databricks_cluster__run_incremental_fail_on_schema_change(self):
        self.run_incremental_fail_on_schema_change()

    @use_profile("databricks_cluster")
    def test__databricks_cluster__run_incremental_sync_all_columns(self):
        self.run_incremental_sync_all_columns()

    @use_profile("databricks_uc_cluster")
    def test__databricks_uc_cluster__run_incremental_ignore(self):
        self.run_incremental_ignore()

    @use_profile("databricks_uc_cluster")
    def test__databricks_uc_cluster__run_incremental_fail_on_schema_change(self):
        self.run_incremental_fail_on_schema_change()

    @use_profile("databricks_uc_cluster")
    def test__databricks_uc_cluster__run_incremental_sync_all_columns(self):
        self.run_incremental_sync_all_columns()

    @use_profile("databricks_uc_sql_endpoint")
    def test__databricks_uc_sql_endpoint__run_incremental_ignore(self):
        self.run_incremental_ignore()

    @use_profile("databricks_uc_sql_endpoint")
    def test__databricks_uc_sql_endpoint__run_incremental_fail_on_schema_change(self):
        self.run_incremental_fail_on_schema_change()

    @use_profile("databricks_uc_sql_endpoint")
    def test__databricks_uc_sql_endpoint__run_incremental_sync_all_columns(self):
        self.run_incremental_sync_all_columns()


class TestDeltaOnSchemaChange(TestIncrementalOnSchemaChange):
    @property
    def project_config(self):
        return {
            "config-version": 2,
            "test-paths": ["tests"],
            "models": {
                "+unique_key": "id",
            },
        }

    @use_profile("databricks_cluster")
    def test__databricks_cluster__run_incremental_ignore(self):
        self.run_incremental_ignore()

    @use_profile("databricks_cluster")
    def test__databricks_cluster__run_incremental_fail_on_schema_change(self):
        self.run_incremental_fail_on_schema_change()

    @use_profile("databricks_cluster")
    def test__databricks_cluster__run_incremental_append_new_columns(self):
        self.run_incremental_append_new_columns()

    @use_profile("databricks_cluster")
    def test__databricks_cluster__run_incremental_sync_all_columns(self):
        self.run_incremental_sync_all_columns()

    @use_profile("databricks_uc_cluster")
    def test__databricks_uc_cluster__run_incremental_ignore(self):
        self.run_incremental_ignore()

    @use_profile("databricks_uc_cluster")
    def test__databricks_uc_cluster__run_incremental_fail_on_schema_change(self):
        self.run_incremental_fail_on_schema_change()

    @use_profile("databricks_uc_cluster")
    def test__databricks_uc_cluster__run_incremental_append_new_columns(self):
        self.run_incremental_append_new_columns()

    @use_profile("databricks_uc_cluster")
    def test__databricks_uc_cluster__run_incremental_sync_all_columns(self):
        self.run_incremental_sync_all_columns()

    @use_profile("databricks_uc_sql_endpoint")
    def test__databricks_uc_sql_endpoint__run_incremental_ignore(self):
        self.run_incremental_ignore()

    @use_profile("databricks_uc_sql_endpoint")
    def test__databricks_uc_sql_endpoint__run_incremental_fail_on_schema_change(self):
        self.run_incremental_fail_on_schema_change()

    @use_profile("databricks_uc_sql_endpoint")
    def test__databricks_uc_sql_endpoint__run_incremental_append_new_columns(self):
        self.run_incremental_append_new_columns()

    @use_profile("databricks_uc_sql_endpoint")
    def test__databricks_uc_sql_endpoint__run_incremental_sync_all_columns(self):
        self.run_incremental_sync_all_columns()
