import os

def cloner(url, response):
    if response != 'dummy':
        striped_url = url.replace('http://','').replace('https://','').rstrip('/')
        splits = striped_url.strip('?')[0].split('/')
        root = splits[0]
        splits.remove(root)
        page = splits[-1]

        try:
            splits.remove(page)
        
        except ValueError:
            pass

        prefix = root + '_copy'

        try:
            os.mkdir(prefix)

        except OSError:
            pass

        suffix = ''

        if splits:
            for dir in splits:
                suffix += dir + '/'

                try:
                    os.mkdir(prefix + '/' + suffix)
                except OSError:
                    pass

        path = prefix + '/' + suffix
        tail = ''

        if '.' not in page:
            tail += '.html'
        
        if page == root:
            name = 'index.html'
        else:
            name = page

        if len(url.split('?')) > 1:
            tail += '?' + url.split('?')[1]

        with open(path + name + tail, 'w+') as o:
            o.write(response.encode('utf-8'))