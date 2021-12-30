import tkinter as tk
import math

def make_voronoi_diagram(sites, xBounds, yBounds):
    sweep_line = yBounds[1]
    beach_line = BeachLine()

    site_event_queue = []
    sites.sort(key = lambda s: s.y)
    for site in sites:
        site_event_queue.append(SiteEvent(site))
    circle_event_queue = []

    def handle_site_event(site_event):
        beach_line.handle_site_event(site_event)
            

class BeachLine:
    def __init__(self):
        self.sites = []

    # returns new circle events
    def handle_site_event(self, site, directrix):
        i = 0       # the index of the site whose curve is directly above *site*
        for j in range(0, self.sites.count()):
            i = j
            if self.get_breakpoint(i, directrix) > site.x:
                break

        # the new site is sandwiched between two occurences of the old site
        old_site = self.sites[i]
        self.sites.insert(i, site)
        self.sites.insert(i, old_site)

        circle_events = []
        if i > 1:
            circle_events.append(CircleEvent(self.sites[i - 2], self.sites[i - 1], self.sites[i]))
        if self.sites.count() > i + 2:
            circle_events.append(CircleEvent(self.sites[i], self.sites[i + 1], self.sites[i + 2]))
        return circle_events

    # returns the breakpoint between *sites[i] and sites[i + 1]*
    def get_breakpoint(self, i, directrix):
        l_point = self.sites[i].point
        r_point = self.sites[i + 1].point
        l_parabola = Parabola(directrix, (l_point.x, l_point.y))
        r_parabola = Parabola(directrix, (r_point.x, r_point.y))

        index = 0
        if l_point.y < r_point.y:
            index = 1
        return l_parabola.intersect_with(r_parabola)[index]

class CircleEvent:
    def __init__(self, l_site, m_site, r_site):
        self.sites = [l_site, m_site, r_site]
        (r, center) = Point.find_circumcircle(l_site.point, m_site.point, r_site.point)
        self.y = center.y - r

class SiteEvent:
    def __init__(self, site):
        self.y = site.point.y
        self.site = site

class Site:
    def __init__(self, point):
        self.point = point

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def get_distance_from(self, point):
        x_diff = self.x - point.x
        y_diff = self.y - point.y
        return math.sqrt(x_diff * x_diff + y_diff * y_diff)

    # returns a (point, float) tuple which holds the center and radius
    @staticmethod
    def find_circumcircle(point_1, point_2, point_3):
        m_1 = (point_1.x - point_2.x) / (point_2.y - point_1.y)
        m_2 = (point_1.x - point_3.x) / (point_3.y - point_1.y)
        midpoint_1 = Point((point_1.x + point_2.x) / 2, (point_1.y + point_2.y) / 2)
        midpoint_2 = Point((point_1.x + point_3.x) / 2, (point_1.y + point_3.y) / 2)
        b_1 = midpoint_1.y - m_1 * midpoint_1.x
        b_2 = midpoint_2.y - m_2 * midpoint_2.x
        x = (b_2 - b_1) / (m_1 - m_2)
        center = Point(x, m_1 * x + b_1)
        r = center.get_distance_from(point_1)
        return (center, r)
        # point slope form: (y - y1) = m(x-x1)
        # slope intercept form: y = m * x + y1 - m * x1
        # intersection: m1x + b1 = m2x + b2

class Helper:
    @staticmethod
    def find_circumcenter(x_1, y_1, x_2, y_2, x_3, y_3):
        m_1 = (x_1 - x_2) / (y_2 - y_1)
        m_2 = (x_1 - x_3) / (y_3 - y_1)

class Parabola:
    def __init__(self, directrix = 0, focus = (0, 0)):
        self.directrix = directrix
        self.focus = focus
        self.vertex = (focus[0], (directrix + focus[1]) / 2)

        directrix_vertex_diff = abs(self.vertex[1] - directrix)
        if directrix_vertex_diff == 0:
            self.a = 0
        else:
            self.a = 1 / 4 / directrix_vertex_diff

        self.b = -2 * self.a * self.focus[0]

        self.c = math.pow(self.focus[0], 2) + self.vertex[1]

    def evaluate(self, x):
        return self.a * math.pow(x - self.focus[0], 2) + self.vertex[1]

    # returns all intersections in ascending order
    def intersect_with(self, parabola):
        a_diff = self.a - parabola.a
        b_diff = self.b - parabola.b
        c_diff = self.c - parabola.c

        determinant = math.pow(b_diff, 2) - 4 * a_diff * c_diff

        if determinant < 0:
            return []
        elif determinant == 0:
            x = -self.b / (2 * self.a)
            return [(x, self.evaluate(x))]
        else:
            sqrt_determinant = math.sqrt(determinant)
            denominator = 2 * self.a
            l_x = (-self.b - sqrt_determinant) / denominator
            r_x = (-self.b + sqrt_determinant) / denominator
            return [(l_x, self.evaluate(l_x)), (r_x, self.evaluate(r_x))]

    def draw_on(self, canvas:tk.Canvas, bounds:tuple[int, int] = None, step_size:int = 1):
        if bounds == None:
            bounds = (0, canvas.winfo_reqwidth())

        # draw directrix
        canvas.create_line(0, self.directrix, canvas.winfo_reqwidth(), self.directrix, dash = (3, 2))

        # draw focus
        canvas.create_oval(self.focus[0] - 2, self.focus[1] - 2, self.focus[0] + 2, self.focus[1] + 2)

        # draw parabola
        if self.directrix == self.focus[1]:
            canvas.create_line(self.focus[0], self.focus[1], self.focus[0], canvas.winfo_reqheight())
            return
        for x in range(bounds[0], bounds[1], step_size):
            canvas.create_line(x, self.evaluate(x), x + step_size, self.evaluate(x + step_size))

if __name__ == "__main__":
    canvas = tk.Canvas(master = None, width = 800, height = 450)
    canvas.pack()

    def start():
        i = 0
        def update():
            nonlocal i
            parabola = Parabola(200 + i % 50, (400, 225))
            canvas.delete("all")
            parabola.draw_on(canvas)
            i += 1

            canvas.after(33, update)
        update()

    canvas.after(0, start)
    canvas.mainloop()
