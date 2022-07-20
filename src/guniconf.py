# for deployment
bind = '0.0.0.0:8000'
workers = 1

# log to stdout - handy for docker
accesslog = '-'

# log to stderr - handy to docker
errorlog = '-'

# provide X-Forwarded-For header for openshift deployment
access_log_format = '%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s %(L)s'
