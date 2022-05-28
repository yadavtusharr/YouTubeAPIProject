"""
Q1. [X] Total subs, videos, views, published date, and Country
Q2. [X] Total length of playlist on channel
Q4. [X] Most viewed, and liked video on the channel.
"""

# Importing the libraries

import googleapiclient.discovery
import pandas as pd
import re
from datetime import timedelta

import matplotlib.pyplot as plt
import seaborn as sns

# Creating a request to connect with YouTube API

api_key = 'ADD YOUR API KEY'

channel_ids = ['UC7cs8q-gJRlGwj4A8OmCmXg',  # Alex The Analyst
               'UCLLw7jmFsvfIVaUFsLs8mlQ',  # luke Barousse
               'UCnz-ZXXER4jOvuED5trXfEA',  # TechTFQ
               'UCJQJAI7IjbLcpsjWdSzYz0Q'  # Thu Vu
               ]

youtube = googleapiclient.discovery.build(
    'youtube', 'v3', developerKey=api_key)


# Creating a function to get channel stats

def get_channel_stats(youtube, channel_ids):
    channel_request = youtube.channels().list(
        part='snippet,contentDetails, statistics',
        id=channel_ids
    )

    channel_response = channel_request.execute()

    # loop to get all channels stats

    ch_stats = []
    for i in channel_response['items']:
        stats = dict(Channel_name=i['snippet']['title'],
                     Published_date=i['snippet']['publishedAt'],
                     Country=i['snippet']['country'],
                     Total_views=i['statistics']['viewCount'],
                     Total_sub=i['statistics']['subscriberCount'],
                     Total_videos=i['statistics']['videoCount'],
                     Playlist_ids=i['contentDetails']['relatedPlaylists']['uploads'])
        ch_stats.append(stats)

    return ch_stats


# Function to get video stats

def get_video_stats(youtube):
    playlist_ids = ['UULLw7jmFsvfIVaUFsLs8mlQ', 'UUnz-ZXXER4jOvuED5trXfEA', 'UUJQJAI7IjbLcpsjWdSzYz0Q',
                    'UU7cs8q-gJRlGwj4A8OmCmXg']
    vid_data = []
    nextPageToken = None
    for ids in playlist_ids:
        while True:
            pl_request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=ids,
                maxResults=50,
                pageToken=nextPageToken
            )

            pl_response = pl_request.execute()

            vid_ids = []
            for item in pl_response['items']:
                vid_ids.append(item['contentDetails']['videoId'])

            vid_request = youtube.videos().list(
                part='snippet, contentDetails, statistics',
                id=','.join(vid_ids)
            )

            vid_response = vid_request.execute()

            for item in vid_response['items']:
                data = dict(Channel_name=item['snippet']['channelTitle'],
                            Video_name=item['snippet']['title'],
                            yt_link=item['id'],
                            video_date=item['snippet']['publishedAt'],
                            duration=item['contentDetails']['duration'],
                            views=item['statistics']['viewCount'],
                            likes=item['statistics']['likeCount'])
                vid_data.append(data)

            nextPageToken = pl_response.get('nextPageToken')

            if not nextPageToken:
                break

    return vid_data


# Function to get total duration of all videos on channel

def get_playlist_duration(youtube):

    playlist_ids = ['UULLw7jmFsvfIVaUFsLs8mlQ', 'UUnz-ZXXER4jOvuED5trXfEA', 'UUJQJAI7IjbLcpsjWdSzYz0Q', 'UU7cs8q-gJRlGwj4A8OmCmXg']

    hours_pattern = re.compile(r'(\d+)H')
    minutes_pattern = re.compile(r'(\d+)M')
    seconds_pattern = re.compile(r'(\d+)S')

    total_seconds = 0
    total_video_time = []
    nextPageToken = None

    for ids in playlist_ids:
        while True:
            pl_request = youtube.playlistItems().list(
                part='snippet, contentDetails',
                playlistId=ids,
                maxResults=50,
                pageToken=nextPageToken
           )

            pl_response = pl_request.execute()

            vid_ids = []
            for i in pl_response['items']:
                vid_ids.append(i['contentDetails']['videoId'])

            vid_request = youtube.videos().list(
                part='snippet, contentDetails',
                id=','.join(vid_ids)
            )

            vid_response = vid_request.execute()

            for i in vid_response['items']:

                duration = i['contentDetails']['duration']

                hours = hours_pattern.search(duration)
                minutes = minutes_pattern.search(duration)
                seconds = seconds_pattern.search(duration)

                hours = int(hours.group(1)) if hours else 0
                minutes = int(minutes.group(1)) if minutes else 0
                seconds = int(seconds.group(1)) if seconds else 0

                video_seconds = timedelta(
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds
                ).total_seconds()

                total_seconds += video_seconds

            nextPageToken = pl_response.get('nextPageToken')

            if not nextPageToken:
                break

        total_seconds = int(total_seconds)
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(total_seconds, 60)

        total_time = f'{hours}:{minutes}:{seconds}'
        total_video_time.append(total_time)

    return total_video_time


# Function to get most viewed Videos

def get_views_videos(youtube):
    playlist_ids = ['UULLw7jmFsvfIVaUFsLs8mlQ', 'UUnz-ZXXER4jOvuED5trXfEA', 'UUJQJAI7IjbLcpsjWdSzYz0Q',
                    'UU7cs8q-gJRlGwj4A8OmCmXg']
    videos = []
    next_page_token = None

    for ids in playlist_ids:
        while True:
            pl_request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=ids,
                maxResults=50,
                pageToken=next_page_token)

            pl_response = pl_request.execute()

            vid_ids = []
            for i in pl_response['items']:
                video_id = i['contentDetails']['videoId']
                vid_ids.append(video_id)

            vid_request = youtube.videos().list(
                part='snippet, statistics',
                id=','.join(vid_ids)
            )
            vid_response = vid_request.execute()

            for item in vid_response['items']:
                channel_name = item['snippet']['channelTitle']
                video_name = item['snippet']['title']
                vid_views = item['statistics']['viewCount']
                vid_id = item['id']
                YT_link = f'www.youtube.com/watch?v={vid_id}'

                videos.append({
                    'channel_name': channel_name,
                    'video_name': video_name,
                    'views': int(vid_views),
                    'url': YT_link
                })

            next_page_token = pl_response.get('nextPageToken')

            if not next_page_token:
                break
    return videos


# Creating DataFrames


channel_stats = pd.DataFrame(get_channel_stats(youtube, channel_ids))
video_stats = pd.DataFrame(get_video_stats(youtube))
viewed_videos = pd.DataFrame(get_views_videos(youtube))
Total_playlist_length = get_playlist_duration(youtube)

# changing data types


# for channel_stats


channel_stats['Channel_name'] = channel_stats['Channel_name'].astype(str)
channel_stats['Country'] = channel_stats['Published_date'].astype(str)
channel_stats['Published_date'] = pd.to_datetime(channel_stats['Published_date'])
channel_stats['Total_views'] = pd.to_numeric(channel_stats['Total_views'])
channel_stats['Total_sub'] = pd.to_numeric(channel_stats['Total_sub'])
channel_stats['Total_videos'] = pd.to_numeric(channel_stats['Total_videos'])
channel_stats['Playlist_ids'] = channel_stats['Playlist_ids'].astype(str)

# for video_stats


video_stats['Channel_name'] = video_stats['Channel_name'].astype(str)
video_stats['Video_name'] = video_stats['Video_name'].astype(str)
video_stats['yt_link'] = video_stats['yt_link'].astype(str)
video_stats['video_date'] = pd.to_datetime(video_stats['video_date'])
video_stats['views'] = pd.to_numeric(video_stats['views'])
video_stats['likes'] = pd.to_numeric(video_stats['likes'])

# for video views

viewed_videos['channel_name'] = viewed_videos['channel_name'].astype(str)
viewed_videos['video_name'] = viewed_videos['video_name'].astype(str)
viewed_videos['url'] = viewed_videos['url'].astype(str)
viewed_videos['views'] = pd.to_numeric(viewed_videos['views'])


# Creating csv file
channel_stats.to_csv('C:\\Users\\asus\\PycharmProjects\\YouTubeAPIProject\\channel_stats.csv')
video_stats.to_csv('C:\\Users\\asus\\PycharmProjects\\YouTubeAPIProject\\video_stats.csv')
viewed_videos.to_csv('C:\\Users\\asus\\PycharmProjects\\YouTubeAPIProject\\viewed_videos.csv')


# Data Analysis

# Q. Total subs, videos, views, published date, and Country

#subs = sns.barplot(x='Channel_name', y='Total_sub', data=channel_stats)

#videos_views = sns.barplot(x='Channel_name', y='Total_views', data=channel_stats)

uploads = sns.barplot(x='Channel_name', y='Total_videos', data=channel_stats)


plt.show()


# Q. Total length of playlist on channelTotal length of playlist on channel

# print(Total_playlist_length[0])


# Q. Most viewed, and liked video on the channel.


# Sort videos by views in descending order

print(viewed_videos.sort_values(by='views', ascending=False)[:10])

print(video_stats.sort_values(by='likes', ascending=False)[:10])
