import boto3 

import time
kinesis = boto3.client('kinesis')
stream_name = "TweetDeliveryStream"
tries = 0
while tries < 100:
    tries += 1
    try:
        response = kinesis.describe_stream(StreamName=stream_name)
        #print(response)
        if response['StreamDescription']['StreamStatus'] == 'ACTIVE':
            print("stream is active")
            shards = response['StreamDescription']['Shards']
            for shard in shards:
                shard_id = shard["ShardId"]
                print (repr(shard))
                shard_it =  kinesis.get_shard_iterator(StreamName=stream_name, ShardId=shard_id, ShardIteratorType='LATEST')["ShardIterator"]
                while True:
                    out = kinesis.get_records(ShardIterator = shard_it, Limit=2)
                    for o in out["Records"]:
                        print (o["Data"])
                    shard_it = out["NextShardIterator"]
    except:
        print('error while trying to describe kinesis stream : %s')