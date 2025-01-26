import re


def parse_m3u(file_path):
    media_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mpg')

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    movies = []
    series = []

    current_entry = {}
    for line in lines:
        line = line.strip()
        if line.startswith('#EXTINF'):
            current_entry = {}
            line = line[len('#EXTINF:-1 '):]
            parts = line.split('",', 1)
            attribute_string = parts[0] + '"'
            name = parts[1].strip()

            attributes = re.findall(r'(\w+)=["\']([^"\']+)["\']', attribute_string)
            for key, value in attributes:
                current_entry[key.strip()] = value.strip()

            current_entry['name'] = name
        elif line.startswith('http') or line.startswith('https'):
            if any(line.lower().endswith(ext) for ext in media_extensions):
                current_entry['url'] = line
                title = current_entry.get('title', '')
                name = current_entry['name']

                if 'Series' in title or re.search(r'\b[Ss][._-]?\s*(\d{1,10})[._-]?\s*E\s*(\d{1,10})\b', name):
                    series.append(current_entry)
                else:
                    movies.append(current_entry)

    return movies, series


def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', '', name).strip()
    name = name.replace('...', '…').replace('..', '…')
    name = name.replace('\t', '').replace('\n', '').strip().rstrip('. ')
    return name

def remove_season_episode_info_full(name):
    # This regex will match one character before 'S' and the full season+episode format 'S01E01'
    name = re.sub(r'.[._-]?[Ss][._-]?\d{1,10}[._-]?[Ee][._-]?\d{1,10}.*', '', name)
    name = re.sub(r'.[._-]?[Ss][._-]?\d{1,10}.*', '', name)
    name = re.sub(r'.[._-]?[Ee][._-]?\d{1,10}.*', '', name)
    return name.strip()

def remove_season_episode_info(name):
    name = re.sub(r'\b[Ss][._-]?(\d{1,10})[._-]?E(\d{1,10})\b', '', name)
    name = re.sub(r'\b[Ss][._-]?(\d{1,10})\b', '', name)
    name = re.sub(r'.[._-]?[Ss][._-]?\d{1,10}.*', '', name)
    name = re.sub(r'.[._-]?[Ee][._-]?\d{1,10}.*', '', name)
    return name.strip()


