import twitter

class ATweets():
    def __init__(self, raw_query):
        self.twitter_api = twitter.Api(consumer_key='fd5TwZfTmZR4Jaaaaaaaaa',
                      consumer_secret='8aFf6eGf6kKEfrIQjsiQbYyveawaaaaaaaaa',
                      access_token_key='14698049-rtGaaaaaaaaa',
                      access_token_secret='Z2qkurxKaaaaaaaaa')
        self.raw_query = raw_query

    def capture(self):
        statuses = self.twitter_api.GetSearch(
            raw_query = self.raw_query,
            lang = 'en',
            count=3, result_type='recent', include_entities=True
        )

        return statuses

