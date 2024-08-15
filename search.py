import argparse 
import csv 
from googleapiclient.discovery import build #for building the YouTube API service
from googleapiclient.errors import HttpError #for handling HTTP errors when accessing Google APIs

# YouTube API credentials
DEVELOPER_KEY = #[INSERT DEVELOPER KEY HERE]
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

#search for results based on criteria
def youtube_search(options):

    #build the YouTube API service
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    # Call the search.list method to retrieve results matching the specified query term.
    search_response = youtube.search().list(
        q=options.q,
        part='id,snippet',
        maxResults=options.max_results
    ).execute()

    videos = []

    #add each result to the videos list, including title, description, author, and views.
    for search_result in search_response.get('items', []):
        video_id = search_result.get('id', {}).get('videoId')
        if video_id:
            video_response = youtube.videos().list(part='statistics', id=video_id).execute()
            video_statistics = video_response.get('items', [])[0].get('statistics', {})
            video_info = {
                'Title': search_result['snippet']['title'],
                'Description': search_result['snippet']['description'],
                'Author': search_result['snippet']['channelTitle'],
                'Views': video_statistics.get('viewCount') if 'viewCount' in video_statistics else None
            }
            videos.append(video_info)

    #verify output - uncomment if needed
    #print('Videos:\n', '\n'.join(video['Title'] for video in videos), '\n')

    #save results to a csv file 
    with open('Results.csv', 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['Title', 'Description', 'Author', 'Views']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(videos)

#error handling
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--q', help='Search term', default='Education Technology')
    parser.add_argument('--max-results', help='Max results', default=100)
    args = parser.parse_args()

    try:
        youtube_search(args)
    except HttpError as e:
        print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
