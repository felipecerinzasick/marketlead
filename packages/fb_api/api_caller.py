import datetime
import time

from facebookads.api import FacebookAdsApi
from facebookads.adobjects.adaccountuser import AdAccountUser
from facebookads.adobjects.adaccount import AdAccount
from facebookads.adobjects.adsinsights import AdsInsights
from facebookads.exceptions import FacebookRequestError

from collections import Counter


class ApiParser():
    fields = [
        AdsInsights.Field.account_currency,
        AdsInsights.Field.account_id,
        AdsInsights.Field.campaign_id,
        # AdsInsights.Field.campaign_name,
        # AdsInsights.Field.adset_name,
        # AdsInsights.Field.ad_name,
        AdsInsights.Field.spend,
        AdsInsights.Field.clicks,
        # AdsInsights.Field.cpc,
        # AdsInsights.Field.ctr,
        AdsInsights.Field.impressions,
        # AdsInsights.Field.cost_per_unique_click,
        AdsInsights.Field.unique_clicks,
    ]

    required_merged_field_list = [
        AdsInsights.Field.spend,
        AdsInsights.Field.clicks,
        AdsInsights.Field.impressions,
        AdsInsights.Field.unique_clicks,
    ]
    final_data = {}

    def __init__(self, token, api_version='v5.0'):
        self.token = token
        self.api_version = api_version
        FacebookAdsApi.init(access_token=self.token, api_version=self.api_version)

    def build_params(self, from_time, to_time):
        if isinstance(from_time, str) and isinstance(to_time, str):
            from_time_str, to_time_str = from_time, to_time
        elif isinstance(from_time, datetime.datetime) and isinstance(to_time, datetime.datetime):
            time_format = '%Y-%m-%d'
            from_time_str, to_time_str = from_time.strftime(time_format), to_time.strftime(time_format)
        else:
            return {}
        return {
            'time_range': {
                'since': from_time_str,
                'until': to_time_str,
            },
            'breakdowns': [],
            'level': 'ad',
            'time_increment': 1
        }

    def get_all_ad_accounts(self):
        """sample_response:: <api.Cursor> [
            <AdAccount> {
                "account_id": "12345",
                "id": "act_12345"
            }, <AdAccount> {
                "account_id": "234567",
                "id": "act_234567"
            }
        ]"""
        try:
            me = AdAccountUser(fbid='me')
            ad_acc = me.get_ad_accounts()
            ad_acc_list = []
            for item_ad_acc in ad_acc._queue:
                ad_acc_list.append({
                    "id": item_ad_acc.get("id"),
                    "account_id": item_ad_acc.get("account_id"),
                })
            return ad_acc_list
        except FacebookRequestError as er:
            print(er)
        return []

    def get_ads_insight(self, account_id, from_time, to_time):
        """sample_response:: <api.Cursor> [
            <AdsInsights> {
                "ad_name": "Ad name here",
                "adset_name": "Sample name",
                "campaign_id": "123456789",
                "campaign_name": "Campaign Test name",
                "cost_per_unique_click": "0.727143",
                "cpc": "0.727143",
                "ctr": "1.62037",
                "date_start": "2019-12-10",
                "date_stop": "2019-12-10",
                "spend": "5.09",
                "clicks": "7",
                "unique_clicks": "7"
            },
        ]"""
        params = self.build_params(from_time, to_time)
        the_ad_account = AdAccount(account_id)
        try:
            async_job = the_ad_account.get_insights_async(fields=self.fields, params=params)
            status = async_job.remote_read()
            while status['async_percent_completion'] < 100:
                time.sleep(1)
                status = async_job.remote_read()
            result = async_job.get_result()

            insight_data_list = []
            for item_ad_insight in result._queue:
                temp_dict = {}
                for _key in self.fields:
                    try:
                        temp_dict.update({_key: item_ad_insight.__getitem__(_key), })
                    except KeyError:
                        temp_dict.update({_key: '', })
                if temp_dict:
                    insight_data_list.append(temp_dict)
            for k in self.required_merged_field_list:
                self.final_data.update({k: self.add_value_by_key(k, insight_data_list)})
            if len(insight_data_list) > 0:
                remaining_fields_set = set(self.fields) ^ set(self.required_merged_field_list)
                for f in remaining_fields_set:
                    # remaining fields has same value of all items of the list. That's why only first item is considered
                    self.final_data.update({f: insight_data_list[0].get(f, '')})
        except FacebookRequestError:
            pass
            # print(er)
        return self.final_data

    @staticmethod
    def add_value_by_key(_key, _data):
        _sum = sum((Counter({el['campaign_id']: float(el[_key])}) for el in _data), Counter())
        for x in _sum.most_common():
            try:
                # _sum is always counter({x, y}), and y is the value, so we need the first
                val = x[1]
                return int(val) if val.is_integer() else val
            except KeyError:
                pass
        return 0
