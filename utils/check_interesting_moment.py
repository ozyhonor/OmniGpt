import random
import re


def choose_good_moment(answers, count_good_moment):
    answers = ''.join(answers)
    pattern = r'(\d{2}:\d{2}->\d{2}:\d{2})\. (.+?)(#.+)'
    good_timestamps = []
    try:
        for match in re.findall(pattern, answers):
            time_code, title, tags = match
            tags = ' '.join(re.findall(r'#\w+', tags[1:]))
            stamps = time_code.split('->')
            stamps = [_.replace(':', '') for _ in stamps]
            print('Временной код:', time_code)
            print('Название:', title.strip())
            print('Теги:', ' '.join(re.findall(r'#\w+', tags[1:])))
            if (stamps[1]-stamps[0]<100) and len(title.strip())>7 and len(tags.split(' '))>2:
                good_timecode = time_code.replace('>', '')
                name = title.strip()
                good_timestamps.append({'time': good_timecode,
                                        'name': name,
                                        'tags': tags})
        if len(good_timestamps)<count_good_moment:
            return good_timestamps
        return [random.choice(good_timestamps) for i in range(0, count_good_moment)]
    except:...
    return good_timestamps
