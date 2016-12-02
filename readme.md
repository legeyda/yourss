

    # generic
    api/v1&...
        url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DaeOzBCbwxUo
        episode=3DaeOzBCbwxUo
        user=ArtemMelnikRu
        channel=asldkfausdf203u9803udawe
        playlist=238jasf98f9flvdfjoidfjLDsds
        type=audio|video
        quality=high|low
        format=...
        links=webpage|direct|proxy
        page_index=1
        page_size=10
        match_title=regex
        ignore_title=regex

    #

    /?youtube_episode=32weofjsa&youtube_query=alsd839wea&url=http://example.com

    # feeds
    api/v1/feed
        url
        type=
        quality
        format
        link_type=webpage|direct|proxy
        page_index=1
        page_size=10
        match_title=regex
        ignore_title=regex
    api/v1/url/playlist/https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DaeOzBCbwxUo/video
    api/v1/youtube/episode?query=search+term+query
    api/v1/youtube/user/ArtemMelnikRu/video
    api/v1/youtube/channel/UC9SN4RokP91W5NipsbGp8mQ/video
    api/v1/youtube/playlist/PLuNSr6LAwDAbhfrIbmu0Nv40Abx3xJUtj/audio

    # episode
    api/v1/episode
        url
        type=audio|video
        quality=high|low
        format=
    api/v1/url/episode/https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DaeOzBCbwxUo[/video]
    api/v1/youtube/episode/aeOzBCbwxUo/audio