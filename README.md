
# M3U4STRM Version 2

## Introduction

This project was created to solve the issue of playing M3U Plus lists on Jellyfin, the program uses a UI to manage M3Us and add media to Jellyfin. 




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


```yaml
services:
  app:
    image: hannayusuf/m3u4strmV2
    container_name: m3u4stream_app
    environment:
      - MONGODB_PWD=${MONGODB_PWD}  # Fill this with your MongoDB password
      - MONGODB_URI=${MONGODB_URI}  # Fill this with your MongoDB URI (in this case m3u4stream_mongodb:27017)
      - MONGODB_USERNAME=${MONGODB_USERNAME}  # Fill this with your MongoDB username
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}  # Fill to set your admin password to access the admin portal
    volumes:
      - /path/to/m3us:/m3us
      - /path/to/results:/results  # Optional in case you want to easily access the strm results
      - /path/to/jellyfin/movies:/jellyfin/movies
      - /path/to/jellyfin/tvshows:/jellyfin/tvshows
    ports:
      - "8001:8001"
      - "3000:3000"
    network_mode: host
    depends_on:
      - mongodb

  mongodb:
    image: mongo:latest
    container_name: m3u4stream_mongodb
    environment:
      - MONGO_INITDB_ROOT_USERNAME=${MONGODB_USERNAME}  # Use the same username as above
      - MONGO_INITDB_ROOT_PASSWORD=${MONGODB_PWD}  # Use the same password as above
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"
    restart: unless-stopped

volumes:
  mongodb_data:
  
```
