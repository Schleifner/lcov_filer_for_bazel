Bazel coverage command doesn't support LCOV_EXCL_START. This filter can help to exclude the ignored lines by filter the lcov file

Usage example:
```shell
mkdir -p bazel-coverage &&\

bazel coverage some_bazel_test_target --action_env=COVERAGE_GCOV_OPTIONS=-b &&\

lcov --rc lcov_branch_coverage=1 --remove "$(bazel info output_path)/_coverage/_coverage_report.dat" '*/tests/*' --output-file bazel-coverage/cov.dat &&\

python3 scripts/lcov_filter.py bazel-coverage/cov.dat &&\

genhtml --branch-coverage bazel-coverage/cov_filtered.dat -o bazel-coverage
```