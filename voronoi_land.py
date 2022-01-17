import tkinter as tk
import math
from typing import Callable
import random as rng
# change
# Responsible for managing sweep line events
def make_voronoi_diagram(sites, x_bounds, y_bounds):
    def handle_site_event(site_event):
        add_circle_events(beach_line.handle_site_event(site_event, sweep_line))
            
    def handle_circle_event(circle_event):
        add_circle_events(beach_line.handle_circle_event(circle_event, sweep_line, edges))
        remove_circle_events(circle_event.arcs[1])

    def add_circle_events(events):
        for event in events:
            ListHelper.sorted_insert(event, circle_event_queue, lambda c: c.y)
            for arc in event.arcs:
                circle_events_by_arc.setdefault(arc, []).append(event)

    # Removes all circle events associated with *arc*
    def remove_circle_events(arc):
        for event in circle_events_by_arc[arc]:
            circle_event_queue.remove(event)

    sweep_line = y_bounds[1]
    beach_line = BeachLine()

    edges = EdgeHolder()
    site_event_queue = []
    sites.sort(key = lambda s: s.point.y)
    for site in sites:
        site_event_queue.append(SiteEvent(site))
    circle_event_queue = []
    circle_events_by_arc = {}

    while True:
        site_event_len = len(site_event_queue)
        circle_event_len = len(circle_event_queue)
        closest_site_y = y_bounds[0] - 1 if site_event_len == 0 else site_event_queue[-1].y
        closest_circle_y = y_bounds[0] - 1 if circle_event_len == 0 else circle_event_queue[-1].y
        if closest_site_y < y_bounds[0] and closest_circle_y < y_bounds[0]:
            break
        if closest_site_y > closest_circle_y:
            sweep_line = closest_site_y
            handle_site_event(site_event_queue.pop())
        else:
            sweep_line = closest_circle_y
            handle_circle_event(circle_event_queue.pop())

    return edges  

class ListHelper:
    # TODO: use a binary search
    # assumes *sorted_list* is sorted descending
    @staticmethod
    def sorted_insert(element, sorted_list:list, key:Callable):
        value = key(element)
        j = 0
        for i in range(0, len(sorted_list)):
            j = i
            if key(sorted_list[i]) < value:
                break
        sorted_list.insert(j, element)

class BeachLine:
    def __init__(self):
        self.arcs = []

    # Returns new circle events
    def handle_site_event(self, site_event, directrix):
        arc = SiteArc(site_event.site)

        # TODO: Binary search
        i = 0       # The index of the site whose curve is directly above *site_event.site*
        for j in range(0, len(self.arcs)):
            i = j
            if self.get_breakpoint(i, directrix) > site_event.site.point.x:
                break

        # The new site is sandwiched between two occurences of the old site
        old_arc = self.arcs[i]
        self.arcs.insert(i, arc)
        self.arcs.insert(i, old_arc)

        circle_events = []
        if i > 1:
            circle_events.append(CircleEvent(self.arcs[i - 2].site, self.arcs[i - 1].site, self.arcs[i].site))
        if len(self.arcs) > i + 2:
            circle_events.append(CircleEvent(self.arcs[i].site, self.arcs[i + 1].site, self.arcs[i + 2].site))
        return circle_events

    def handle_circle_event(self, circle_event, directrix, edge_holder):
        endpoint = self.get_breakpoint(self.arcs.index(circle_event.arcs[0]), directrix)
        edge_holder.push_endpoint(circle_event.sites[0], circle_event.sites[1], endpoint)
        edge_holder.push_endpoint(circle_event.sites[1], circle_event.sites[2], endpoint)
        
        new_circle_events = []
        i = self.arcs.index(circle_event.arcs[1])
        if i > 1 and i < len(self.arcs) - 1:
            new_circle_events.append(CircleEvent(self.arcs[i - 2], self.arcs[i - 1], self.arcs[i + 1]))
        if i > 0 and i < len(self.arcs) - 2:
            new_circle_events.append(CircleEvent(self.arcs[i - 1], self.arcs[i + 1]), self.arcs[i + 2])
        return new_circle_events

    # Returns the breakpoint between *arcs[i] and arcs[i + 1]*
    def get_breakpoint(self, i, directrix):
        l_point = self.arcs[i].site.point
        r_point = self.arcs[i + 1].site.point
        l_parabola = Parabola(directrix, (l_point.x, l_point.y))
        r_parabola = Parabola(directrix, (r_point.x, r_point.y))

        index = 0
        if l_point.y < r_point.y:
            index = 1
        return l_parabola.intersect_with(r_parabola)[index]

class CircleEvent:
    def __init__(self, l_arc, m_arc, r_arc):
        self.arcs = [l_arc, m_arc, r_arc]
        self.sites = [l_arc.site, m_arc.site, r_arc.site]
        (r, center) = Point.find_circumcircle(self.sites[0].point, self.sites[1].point, self.sites[2].point)
        self.y = center.y - r

class SiteEvent:
    def __init__(self, site):
        self.y = site.point.y
        self.site = site

class Site:
    def __init__(self, point):
        self.point = point

    def make_random_site(x_bounds, y_bounds):
        x = rng.randrange(x_bounds[0], x_bounds[1])
        y = rng.randrange(y_bounds[0], y_bounds[1])
        return Site(Point(x, y)) 

# One site may appear in the beachline more than once -- this wrapper exists to differentiate them so that the 
#   appropriate events can be removed from the circle_event_queue
class SiteArc:
    def __init__(self, site):
        self.site = site

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def get_distance_from(self, point):
        x_diff = self.x - point.x
        y_diff = self.y - point.y
        return math.sqrt(x_diff * x_diff + y_diff * y_diff)

    # Returns a (point, float) tuple which cointains the center and radius
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
        # Point slope form: (y - y1) = m(x-x1)
        # Slope intercept form: y = m * x + y1 - m * x1
        # Intersection: m1x + b1 = m2x + b2

class Edge:
    def __init__(self, start:Point, end:Point, site):
        self.start = start
        self.end = end
        self.site = site

class EdgeHolder:
    def __init__(self):
        self.endpoints_by_sites = {}
        self.edges_by_sites = {}

    def push_endpoint(self, site_1:Site, site_2:Site, endpoint:Point):
        self.endpoints_by_sites.setdefault((site_1, site_2), []).append(endpoint)
        self.endpoints_by_sites.setdefault((site_2, site_1), []).append(endpoint)
        endpoint_list = self.endpoints_by_sites((site_1, site_2))
        if len(endpoint_list) == 2:
            edge = Edge(endpoint_list[0], endpoint_list[1])
            self.edges_by_sites[(site_1, site_2)] = edge
            self.edges_by_sites[(site_2, site_1)] = edge

    def get_edge(self, site_1, site_2):
        return self.edges_by_sites[(site_1, site_2)]

    def get_all_edges(self):
        return list(dict.fromkeys(self.edges_by_sites.items))

    def draw_on(self, canvas):
        for edge in self.get_all_edges():
            canvas.create_line(edge.start.x, edge.start.y, edge.end.x, edge.end.y)

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

    def evaluate(self, x:float):
        return self.a * math.pow(x - self.focus[0], 2) + self.vertex[1]

    # Returns all intersections in ascending x order
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

        # Draw directrix
        canvas.create_line(0, self.directrix, canvas.winfo_reqwidth(), self.directrix, dash = (3, 2))

        # Draw focus
        canvas.create_oval(self.focus[0] - 2, self.focus[1] - 2, self.focus[0] + 2, self.focus[1] + 2)

        # Draw parabola
        if self.directrix == self.focus[1]:
            canvas.create_line(self.focus[0], self.focus[1], self.focus[0], canvas.winfo_reqheight())
            return
        for x in range(bounds[0], bounds[1], step_size):
            canvas.create_line(x, self.evaluate(x), x + step_size, self.evaluate(x + step_size))

if __name__ == "__main__":
    canvas = tk.Canvas(master = None, width = 800, height = 450)
    canvas.pack()

    def start():
        x_bounds = [0, canvas.winfo_reqwidth()]
        y_bounds = [0, canvas.winfo_reqheight()]
        sites = []
        for i in range(0, 10):
            sites.append(Site.make_random_site(x_bounds, y_bounds))
        make_voronoi_diagram(sites, x_bounds, y_bounds)
        
        def update():
            pass
        update()

    canvas.after(0, start)
    canvas.mainloop()
