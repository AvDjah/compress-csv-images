broker_url = 'pyamqp://guest@localhost//'
result_backend = 'db+sqlite:///results.sqlite'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Kolkata'
enable_utc = True