from pandas import DataFrame
from scipy.stats import f


class AnovaDataFrame(DataFrame):
    """
    Subclass of pandas DataFrame implementing ANOVA methods
    """

    def anova(self, group_column, columns=None):
        """
        Calculate one way ANOVAs of the effect of the effect of the group column on the dependent variables in columns
        :param group_column: (str, int, pandas column object) Specifies the independent variable column
        :param columns: (list) List of the dependent variables to analyze the effect of the independent variable on.
        If none, function uses all columns in the input besides the group column as dependent variables.
        :return: pandas DataFrame containing the F-scores and p value for the test of each dependent variable.
        """
        if columns:
            pass
        else:
            columns = self.drop(labels=[group_column], axis=1).columns

        result = DataFrame(data=None, index=columns,
                           columns=['p_value', 'f_statistic', 'mean_variance_between', 'mean_variance_within', ])

        def weighted_sum(func_data):
            """
            Return the mean of a series multiplied by the number of items in the series.
            :param func_data: (pandas Series) input data
            :return:
            """
            return func_data.mean() * func_data.count()

        for dep_variable in columns:
            data = self.dropna(axis=0, how='any', subset=[dep_variable])
            data.loc[:, dep_variable] = data.loc[:, dep_variable].astype(float)
            n_groups = data.loc[:, group_column].unique().shape[0]
            total_n = data.loc[:, dep_variable].count()

            df1 = n_groups - 1
            df2 = total_n - n_groups

            grand_mean = sum(data.groupby(group_column)[dep_variable].agg(weighted_sum)) / total_n

            # Calculate the amount of variance between different sub groups
            ss_between = sum(
                data.groupby(group_column).count()[dep_variable] * (
                    data.groupby(group_column).mean()[dep_variable] - grand_mean
                ) ** 2)

            # Calculate the amount of variance within different sub groups
            ss_within = sum(df2 * data.groupby(group_column).var()[dep_variable])

            # Get the weighted mean variance by dividing by the degrees of freedom
            ms_between = ss_between / df1
            ms_within = ss_within / df2

            # Calculate the f statistic for this hypothesis
            f_statistic = ms_between / ms_within

            # Calculate the p_value given the F statistic

            p_value = f.sf(f_statistic, df1, df2)

            result.loc[dep_variable, 'mean_variance_between'] = ms_between
            result.loc[dep_variable, 'mean_variance_within'] = ms_within
            result.loc[dep_variable, 'f_statistic'] = f_statistic
            result.loc[dep_variable, 'p_value'] = p_value

        return result

    pass
