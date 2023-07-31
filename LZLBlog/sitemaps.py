from django.contrib.sitemaps import Sitemap

class IndexSitemap(Sitemap):
    changefreq = "never"
    priority = 0.6

    def items(self):
        return ['index', 'about']

    def location(self, item):
        return "/index/{}/".format(item)
    
class LoginSitemap(Sitemap):
    changefreq = "never"
    priority = 0.2

    def items(self):
        return ['login', 'register', 'logout', 'reset', 'confirm', 'resetpassword']
    
    def location(self, item):
        return "/login/{}/".format(item)
    
class ListSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return ['blogs', 'works']
    
    def location(self, item):
        return "/{}/list/1/".format(item)