'''
Made by Thomas Wakin
May 7th, 2018

'''

import tweepy
import csv
import json



############## Other functions ################
def chunk(lst, chunk_size):
    '''
    :param lst: any list
    :param chunk_size: integer
    :return: List of lists, where each nested list is the length of chunk_size

    If chunk_size is greater than or equal to length of input list, original list is returned

    If length of input list is not divisible evenly by chunk_size, final list of lists is the remainder
    of input list length and chunk size.
    '''

    # Checks if chunk_size is correct type
    assert isinstance(chunk_size, int)

    # Clause for when chunk_size is greater than or equal to length of list
    if chunk_size >= len(lst):
        return lst

    # Loops through list at intervals of chunk size, append slices of original list to new list
    lst_of_lsts = []
    for i in range(0, len(lst), chunk_size):
        lst_of_lsts.append(lst[i:i + chunk_size])

    return lst_of_lsts

########## Wrapper ###########
class Utils():
    '''
    Class made to hold helper functions.
    Contains methods to go from a list of tweets to several data structures.

    Allows for input of Twitter authentication codes. Can be reused to leverage multiple accounts.
    To paralleize data extraction, create multiple Twitter accounts and instantiate Utils class with new log in info.
    con_key = CONSUMER_KEY
    con_sec = CONSUMER_SECRET
    acc_tok = ACCESS_TOKEN
    acc_tok_sec = ACCESS_TOKEN_SECRET
    '''
    def __init__(self, con_key = False, con_sec = False, acc_tok = False, acc_tok_sec = False):
        self.con_key = con_key
        self.con_sec = con_sec
        self.acc_tok = acc_tok
        self.acc_tok_sec = acc_tok_sec

        auth = tweepy.OAuthHandler(con_key, con_sec)
        auth.set_access_token(acc_tok, acc_tok_sec)
        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)



    def tweet_ID_to_list(self, chunk_size, tweet_id_list):
        '''
        :param chunk_size: integer
        :param tweet_id_list: list of tweet IDs
        :return: List of tweet objects in JSON format

        Converts a list of tweet IDs to tweet objects.
        Converts those tweet objects to JSON format.
        Returns list of tweets in JSON format

        This function chunks the list of tweets to ensure each call to the Twitter API does not exceed the rate limit
        by being passed too many IDs at once. Also speeds up runtime by not passing each ID individually.

        Recommended chunk size: 100
        '''

        # Chunk list of tweets into smaller chunks
        chunked_ids = chunk(tweet_id_list, chunk_size)

        # Empty list to hold tweet objects
        tweet_objects = []

        # Look up tweets in chunks and add to list
        for chunk in chunked_ids:
            tweets = self.api.statuses_lookup(id_=chunk)
            tweet_objects.append(tweets)

        # Collapse list of lists of tweet objects to one list
        tweet_objects_flat = [item for sublist in tweet_objects for item in sublist]

        # Final list
        tweet_list = []

        # Convert tweet objects to JSON
        for i in range(len(tweet_objects_flat)):
            tweet_list.append(tweet_objects_flat[i]._json)

        return tweet_list

    def get_unique_users(self, tweet_list):
        '''
        :param tweet_list: List of tweet objects in JSON form
        :return: good_user_objects: List of unique users with available accounts, in JSON format
        :return: good_user_IDs: List of unique user IDs with available accounts
        :return: user_dict: Dictionary where key is unique user ID and value is list of user's tweets as IDs

        First, gets all users who have tweets in tweet list.
        Then, identifies all users who have accessible accounts, stores their tweet object as JSON.
        Finally, creates dictionary where key is unique user ID and value is list of user's tweets as IDs
        '''

        unique_users = []
        user_dict = {}

        for tweet in tweet_list:

            # Create list of unique users
            if tweet['user']['id'] in unique_users:
                pass
            else:
                unique_users.append(tweet['user']['id'])

        good_user_objects = []
        good_user_IDs =[]
        for u in unique_users:
            try:
                user_object = self.api.lookup_users([u])
                good_user_objects.append(user_object._json)
                good_user_IDs.append(u)
            except: pass

        for tweet in tweet_list:
            # Create dictionary where key is user and value is list of tweet ids
            if tweet['user']['id'] in user_dict and tweet['user']['id'] in good_user_IDs:
                user_dict[tweet['user']['id']].append(tweet['id'])
            elif tweet['user']['id'] in good_user_IDs and tweet['user']['id'] not in user_dict:
                user_dict[tweet['user']['id']] = [tweet['id']]


        return good_user_objects, good_user_IDs, user_dict


    def get_user_tweets(self, user_id):
        '''

        :param user_id: Twitter user ID
        :return: list of user's past tweets in JSON format

        Creates a tweepy Cursor object to loop through user's tweets.
        Appends tweets to list and returns that list.
        '''
        sn = self.api.get_user(user_id).screen_name
        cursor = tweepy.Cursor(self.api.user_timeline, screen_name=sn).items()

        status_list = []

        for status in cursor:
            status_list.append(status._json)

        return status_list

    def users_timelines(self, list_of_user_ids):
        '''

        :param list_of_user_ids: list of twitter user IDs
        :return: dictionary with user ID as key and list of their most recent tweets as value

        Loops through list of user IDs and calls get_user_tweets.
        Creates dictionary with user ID as key and value as that list of tweets.
        prints check at every 25 users.
        '''

        print("Getting Timelines...")
        status_dict = {}
        counter = 0
        for u in list_of_user_ids:
            time_line = self.get_user_tweets(u)
            status_dict[u] = time_line
            counter +=1
            if counter % 25 == 0:
                print(counter, "users processed")

        return status_dict

    def get_user_followers(self, user_id):
        '''

        :param user_id: Twitter user ID
        :return: list of user's followers as IDs

        Creates a tweepy Cursor object to loop through user's followers.
        Appends follower ID to list and returns that list.
        '''
        sn = self.api.get_user(user_id).screen_name
        cursor = tweepy.Cursor(self.api.followers_ids, screen_name=sn).items()

        follower_list = []

        for follower in cursor:
            follower_list.append(follower)

        return  follower_list

    def users_followers(self, list_of_user_ids):
        '''

        :param list_of_user_ids: list of twitter user IDs
        :return: dictionary with user ID as key and list of their followers as value

        Loops through list of user IDs and calls get_user_followers.
        Creates dictionary with user ID as key and value as list of IDs of that user's followers.
        prints check at every 25 users.
        '''
        print("Getting Followers...")
        follower_dict = {}
        counter = 0
        for u in list_of_user_ids:
            follower_list = self.get_user_followers(u)
            follower_dict[u] = follower_list
            counter += 1
            if counter % 25 == 0:
                print(counter, "users processed")

        return follower_dict


    def get_user_friends(self, user_id):
        '''

        :param user_id: Twitter user ID
        :return: list of user's friends as IDs

        Creates a tweepy Cursor object to loop through user's friends.
        Appends friend ID to list and returns that list.
        '''
        sn = self.api.get_user(user_id).screen_name
        cursor = tweepy.Cursor(self.api.friends_ids, screen_name=sn).items()

        friends_list = []

        for friend in cursor:
            friends_list.append(friend)

        return friends_list


    def users_friends(self, list_of_user_ids):
        '''

        :param list_of_user_ids: list of twitter user IDs
        :return: dictionary with user ID as key and list of their friends as value

        Loops through list of user IDs and calls get_user_friends.
        Creates dictionary with user ID as key and value as list of IDs of that user's friends.
        prints check at every 25 users.
        '''
        print("Getting Friends...")
        friend_dict = {}
        counter = 0
        for u in list_of_user_ids:
            friend_list = self.get_user_friends(u)
            friend_dict[u] = friend_list
            counter +=1
            if counter % 25 == 0:
                print(counter, "users processed")


        return friend_dict