# Example file showing a circle moving on screen
import pygame as pg
import math
import random
import numpy as np
import matplotlib.pyplot as plt

pg.init()

W, H = 800, 800
WIN = pg.display.set_mode((W, H))

pg.display.set_caption('The 3 Body Problem')



# Colors

GREY = (128, 128, 128)
YELLOW = (165,125,27)
BLUE =  (0, 0 , 255)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
CARAMEL = (255, 181, 112)
DARK_BLUE = (0, 0, 139)
WHITE = (255, 255, 255)
DARK_GRAY = (64, 64, 64)




class Planets: 
    AU = 149.6e6 * 1000
    G = 6.67428e-11
    SCALE = 50 / AU
    TIMESTEP = 3600*24


    def __init__(self, x, y, radius, color, mass): 
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass

        self.orbit = []
        self.sun = False
        self.distance_to_sun = 0

        self.x_vel = 0
        self.y_vel = 0
    
    def draw(self, win):
        x = self.x * self.SCALE + W / 2
        y = self.y * self.SCALE + H / 2

        if len(self.orbit) > 2:
            update_points = []
            for point in self.orbit:
                x, y  = point
                x = x * self.SCALE + W / 2
                y = y * self.SCALE + H / 2
                update_points.append((x, y))

            pg.draw.lines(win, self.color, False, update_points, 2)

        pg.draw.circle(win, self.color, (x, y), self.radius)

      


    def attraction (self, other):
        other_x, other_y = other.x , other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x**2 + distance_y**2)

        if other.sun:
            self.distance_to_sun = distance
        
        force = self.G * self.mass * other.mass / distance ** 2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta)*force
        force_y= math.sin(theta)*force
        return force_x, force_y

    def update_position(self, planets):
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue
            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy
        
        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP

        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y))




def generate_random_conditions():
    # Random positions within a reasonable range
    x1 = random.uniform(-0.5, 0.5) * Planets.AU
    y1 = random.uniform(-0.5, 0.5) * Planets.AU
    x2 = random.uniform(-0.5, 0.5) * Planets.AU
    y2 = random.uniform(-0.5, 0.5) * Planets.AU
    x3 = random.uniform(-0.5, 0.5) * Planets.AU
    y3 = random.uniform(-0.5, 0.5) * Planets.AU
    
    # Random velocities (keeping them relatively low for stability)
    v1 = random.uniform(-25, 25) * 1000
    v2 = random.uniform(-25, 25) * 1000
    v3 = random.uniform(-25, 25) * 1000
    
    # Random masses (keeping them in reasonable proportions)
    m1 = random.uniform(0.8, 1.2) * 10**30
    m2 = random.uniform(0.2, 0.4) * 10**30
    m3 = random.uniform(0.2, 0.4) * 10**30
    
    return (x1, y1, v1, m1), (x2, y2, v2, m2), (x3, y3, v3, m3)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pg.font.Font(None, 36)
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pg.draw.rect(surface, color, self.rect)
        pg.draw.rect(surface, WHITE, self.rect, 2)  # White border
        
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pg.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class StabilityPredictor:
    def __init__(self):
        self.stability_threshold = 0.7
        
    def calculate_energy(self, bodies):
        # Calculate total energy of the system
        kinetic_energy = 0
        potential_energy = 0
        
        for i, body1 in enumerate(bodies):
            # Kinetic energy
            v = math.sqrt(body1.x_vel**2 + body1.y_vel**2)
            kinetic_energy += 0.5 * body1.mass * v**2
            
            # Potential energy
            for j, body2 in enumerate(bodies):
                if i != j:
                    dx = body1.x - body2.x
                    dy = body1.y - body2.y
                    r = math.sqrt(dx**2 + dy**2)
                    potential_energy -= Planets.G * body1.mass * body2.mass / r
        
        return kinetic_energy + potential_energy
    
    def calculate_angular_momentum(self, bodies):
        # Calculate total angular momentum
        total_L = 0
        for body in bodies:
            r = math.sqrt(body.x**2 + body.y**2)
            v = math.sqrt(body.x_vel**2 + body.y_vel**2)
            total_L += body.mass * r * v
        return total_L
    
    def predict_stability(self, bodies):
        # Calculate system parameters
        energy = self.calculate_energy(bodies)
        angular_momentum = self.calculate_angular_momentum(bodies)
        
        # Calculate mass ratios
        masses = [body.mass for body in bodies]
        mass_ratios = [m/masses[0] for m in masses[1:]]
        
        # Calculate velocity ratios
        velocities = [math.sqrt(body.x_vel**2 + body.y_vel**2) for body in bodies]
        velocity_ratios = [v/velocities[0] for v in velocities[1:]]
        
        # Calculate position ratios
        positions = [math.sqrt(body.x**2 + body.y**2) for body in bodies]
        position_ratios = [p/positions[0] for p in positions[1:]]
        
        # Stability score calculation
        stability_score = 0
        
        # Energy stability (negative total energy is more stable)
        if energy < 0:
            stability_score += 0.3
        
        # Angular momentum stability
        if angular_momentum > 0:
            stability_score += 0.2
        
        # Mass ratio stability (prefer hierarchical systems)
        if all(0.1 <= ratio <= 0.5 for ratio in mass_ratios):
            stability_score += 0.2
        
        # Velocity ratio stability
        if all(0.5 <= ratio <= 1.5 for ratio in velocity_ratios):
            stability_score += 0.15
        
        # Position ratio stability
        if all(0.3 <= ratio <= 0.7 for ratio in position_ratios):
            stability_score += 0.15
        
        return stability_score >= self.stability_threshold, stability_score

def main():
    run = True
    clock = pg.time.Clock()
    
    # Create restart button
    restart_button = Button(W - 120, 20, 100, 40, "Restart", DARK_GRAY, GREY)
    
    # Create stability predictor
    stability_predictor = StabilityPredictor()
    
    # Generate random initial conditions
    (x1, y1, v1, m1), (x2, y2, v2, m2), (x3, y3, v3, m3) = generate_random_conditions()
    
    # Create three bodies with random initial conditions
    body1 = Planets(x1, y1, 15, RED, m1)
    body1.sun = True
    body1.y_vel = v1
    
    body2 = Planets(x2, y2, 10, BLUE, m2)
    body2.y_vel = v2
    
    body3 = Planets(x3, y3, 10, YELLOW, m3)
    body3.y_vel = v3
    
    planets = [body1, body2, body3]
    
    # Predict initial stability
    is_stable, stability_score = stability_predictor.predict_stability(planets)
    
    while run:
        clock.tick(60)
        WIN.fill((0,0,0))
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    # Generate new random conditions
                    (x1, y1, v1, m1), (x2, y2, v2, m2), (x3, y3, v3, m3) = generate_random_conditions()
                    
                    # Reset bodies with new conditions
                    body1.x = x1
                    body1.y = y1
                    body1.y_vel = v1
                    body1.mass = m1
                    body1.orbit = []
                    
                    body2.x = x2
                    body2.y = y2
                    body2.y_vel = v2
                    body2.mass = m2
                    body2.orbit = []
                    
                    body3.x = x3
                    body3.y = y3
                    body3.y_vel = v3
                    body3.mass = m3
                    body3.orbit = []
                    
                    # Predict stability for new configuration
                    is_stable, stability_score = stability_predictor.predict_stability(planets)
            
            # Handle button events
            if restart_button.handle_event(event):
                # Generate new random conditions
                (x1, y1, v1, m1), (x2, y2, v2, m2), (x3, y3, v3, m3) = generate_random_conditions()
                
                # Reset bodies with new conditions
                body1.x = x1
                body1.y = y1
                body1.y_vel = v1
                body1.mass = m1
                body1.orbit = []
                
                body2.x = x2
                body2.y = y2
                body2.y_vel = v2
                body2.mass = m2
                body2.orbit = []
                
                body3.x = x3
                body3.y = y3
                body3.y_vel = v3
                body3.mass = m3
                body3.orbit = []
                
                # Predict stability for new configuration
                is_stable, stability_score = stability_predictor.predict_stability(planets)
        
        for planet in planets:
            planet.update_position(planets)
            planet.draw(WIN)
        
        # Draw the restart button
        restart_button.draw(WIN)
        
        # Display stability prediction
        font = pg.font.Font(None, 36)
        stability_text = f"Stability: {'Stable' if is_stable else 'Unstable'} ({stability_score:.2f})"
        text_surface = font.render(stability_text, True, WHITE)
        WIN.blit(text_surface, (20, 20))
        
        pg.display.update()
    
    pg.quit()

main()