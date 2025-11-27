
# M3U4STRM Version 2

## Introduction

This project was created to solve the issue of playing M3U Plus lists on Jellyfin, the program uses a UI to manage M3Us and add media to Jellyfin. 
** I used AI in this project mostly in the frontend



## Features

- Upload M3Us to load into Jellyfin
- Load M3Us into the MongoDB database 
- Creates a compatible Jellyfin structure of .strm files 
- Check if the provider's link works 
- Unload Providers from the app
- Move selected media to Jellyfin using a WatchList
- The ability to add individual episodes, shows and seasons
- Get Media Information from the .strm file
- Search bar and page



## Demo

![Image](https://i.ibb.co/znx0M5m/img1.png)
![Image](https://i.ibb.co/4Rgbw51/img2.png)
![Image](https://i.ibb.co/xhQM3tM/img3.png)
![Image](https://i.ibb.co/zx299Rm/img4.png)

## Deployment using Docker Compose
Docker file repository: https://hub.docker.com/repository/docker/hannayusuf/m3u4strm
Below are only example inputs please use yours! 
```yaml
services:
  app:
    image: hannayusuf/m3u4strm:newV3
    container_name: m3u4stream_app
    environment:
      - MONGODB_USERNAME=db_user # Write some user
      - MONGODB_PWD=supersecretpassword
      - MONGODB_URI=m3u4stream_mongodb:27017
      - ADMIN_PASSWORD=supersecretadminpassword
      - JELLYFIN_URL=http://jellyfin-ip:8096 # Enter your jellyfin ip address (important! use your local ip + port)
    volumes:
      - /path/to/your/m3us:/m3us # Optional, provides easy access
      - /path/to/your/results:/results # Optional, provides easy access
      - /path/to/your/jellyfin/movies:/jellyfin/movies # Make sure this is binded to your Jellyfin directory!
      - /path/to/your/jellyfin/tvshows:/jellyfin/tvshows # Make sure this is binded to your Jellyfin directory!
    ports:
      - "8001:8001"
      - "5173:5173"
    depends_on:
      - mongodb
    networks:
      - m3u4stream_net

  mongodb:
    image: mongo:latest
    container_name: m3u4stream_mongodb
    environment:
      - MONGO_INITDB_ROOT_USERNAME=db_user
      - MONGO_INITDB_ROOT_PASSWORD=supersecretpassword
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"
    networks:
      - m3u4stream_net
    restart: unless-stopped

volumes:
  mongodb_data:

networks:
  m3u4stream_net:
    driver: bridge

  
```
