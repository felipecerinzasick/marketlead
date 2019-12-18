import datetime
import time

from facebookads.api import FacebookAdsApi
from facebookads.adobjects.adaccountuser import AdAccountUser
from facebookads.adobjects.adaccount import AdAccount
from facebookads.adobjects.adsinsights import AdsInsights
from facebookads.exceptions import FacebookRequestError


class ApiParser():
    fields = [
        AdsInsights.Field.account_currency,
        AdsInsights.Field.campaign_id,
        AdsInsights.Field.campaign_name,
        AdsInsights.Field.adset_name,
        AdsInsights.Field.ad_name,
        AdsInsights.Field.spend,
        AdsInsights.Field.clicks,
        AdsInsights.Field.cpc,
        AdsInsights.Field.ctr,
        AdsInsights.Field.cost_per_unique_click,
        AdsInsights.Field.unique_clicks,
    ]

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

    def get_ad_account(self):
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
            ads_data_list = []
            for item_ad_insight in result._queue:
                ads_data_list.append({
                    "campaign_id": item_ad_insight.__getitem__('campaign_id'),
                    "cost_per_unique_click": item_ad_insight.__getitem__('cost_per_unique_click'),
                    "cpc": item_ad_insight.__getitem__('cpc'),
                    "ctr": item_ad_insight.__getitem__('ctr'),
                    "unique_clicks": item_ad_insight.__getitem__('unique_clicks'),
                })
            return ads_data_list
        except FacebookRequestError as er:
            print(er)
        return []


