import pygame
import random
import sys
import os
from pygame.locals import *
import json
import math
import openai
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize PyGame
pygame.init()
pygame.mixer.init()

# Set to full screen
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Mystic Tarot Reader")

# Colors - updated with more mystical palette
WHITE = (255, 255, 255)
BLACK = (10, 10, 20)
DARK_PURPLE = (40, 5, 60)
PURPLE = (80, 20, 100)
LIGHT_PURPLE = (180, 150, 220)
GOLD = (212, 175, 55)
DARK_GOLD = (160, 130, 40)
STARLIGHT = (220, 220, 255)
MOONLIGHT = (200, 220, 255)

# Fonts - using more mystical fonts if available, otherwise fall back to default
try:
    title_font = pygame.font.Font("fonts/mystical.ttf", 60)
    font = pygame.font.Font("fonts/mystical.ttf", 36)
    small_font = pygame.font.Font("fonts/mystical.ttf", 30)
    meaning_font = pygame.font.Font("fonts/mystical.ttf", 32)
except:
    title_font = pygame.font.Font(None, 60)
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 30)
    meaning_font = pygame.font.Font(None, 32)

# Card dimensions - made significantly larger
CARD_WIDTH, CARD_HEIGHT = 300, 500

# Load background image or create gradient
def create_background():
    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill(DARK_PURPLE)
    
    # Draw stars
    for _ in range(200):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(1, 3)
        brightness = random.randint(150, 255)
        color = (brightness, brightness, brightness)
        pygame.draw.circle(bg, color, (x, y), size)
    
    # Draw subtle cosmic glow
    for i in range(3):
        center_x = random.randint(0, WIDTH)
        center_y = random.randint(0, HEIGHT)
        radius = random.randint(100, 300)
        alpha = random.randint(10, 30)
        s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*LIGHT_PURPLE, alpha), (radius, radius), radius)
        bg.blit(s, (center_x - radius, center_y - radius))
    
    return bg

background = create_background()

# Tarot Deck (Complete 78 cards)
major_arcana = [
    "0 The Fool", "I The Magician", "II The High Priestess", "III The Empress", 
    "IV The Emperor", "V The Hierophant", "VI The Lovers", "VII The Chariot", 
    "VIII Strength", "IX The Hermit", "X Wheel of Fortune", "XI Justice", 
    "XII The Hanged Man", "XIII Death", "XIV Temperance", "XV The Devil", 
    "XVI The Tower", "XVII The Star", "XVIII The Moon", "XIX The Sun", 
    "XX Judgement", "XXI The World"
]

suits = ["Wands", "Cups", "Swords", "Pentacles"]
ranks = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Page", "Knight", "Queen", "King"]
minor_arcana = [f"{rank} of {suit}" for suit in suits for rank in ranks]

full_deck = major_arcana + minor_arcana

with open('card_meanings.json', 'r') as f:
    card_meanings = json.load(f)

# Spread types
SPREAD_SINGLE = 1
SPREAD_THREE = 2
SPREAD_CELTIC = 3






class TarotCard:
    
    
    
    def __init__(self, name):
        self.name = name
        # Load meanings from the JSON structure
        meanings = card_meanings.get(name, {})
        self.upright = meanings.get('upright', "No meaning available.")
        self.reversed_meaning = meanings.get('reversed', "No reversed meaning available.")
        self.image_filename = meanings.get('image', None)  # Store the image filename
        self.image = self.create_card_image()
        self.reversed = random.random() < 0.2  # 20% chance to be reversed
        self.glow_phase = random.uniform(0, 2 * math.pi)  # For pulsing glow effect
        
        
        
    def update(self):
        # Update glow effect
        self.glow_phase = (self.glow_phase + 0.05) % (2 * math.pi)
        
        
        
    def create_card_image(self):
        """Create a card image with background color and card image"""
        surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        
        # Set background color based on card type
        if self.name in major_arcana:
            top_color = (random.randint(50, 100), random.randint(20, 60), random.randint(80, 120))
            bottom_color = (top_color[0]//2, top_color[1]//2, top_color[2]//2)
        else:
            if "Wands" in self.name:
                top_color = (200, 150, 50)  # Orange
                bottom_color = (150, 70, 20)  # Darker orange
            elif "Cups" in self.name:
                top_color = (50, 120, 200)  # Blue
                bottom_color = (20, 70, 150)  # Deeper blue
            elif "Swords" in self.name:
                top_color = (180, 180, 200)  # Silver
                bottom_color = (120, 120, 150)  # Darker silver
            else:  # Pentacles
                top_color = (150, 120, 50)  # Earthy gold
                bottom_color = (100, 80, 20)  # Darker earth
        
        # Draw gradient background
        for y in range(CARD_HEIGHT):
            ratio = y / CARD_HEIGHT
            r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
            g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
            b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
            pygame.draw.line(surf, (r, g, b), (0, y), (CARD_WIDTH, y))
        
        # Try to load card image if filename exists
        if self.image_filename:
            try:
                # Get the full path to the image
                image_path = os.path.join(os.path.dirname(__file__), "card_images", self.image_filename)
                
                # Load and convert the image
                card_img = pygame.image.load(image_path).convert_alpha()
                card_img = pygame.transform.scale(card_img, (CARD_WIDTH - 40, CARD_HEIGHT - 100))
                
                # Apply the image to the card surface
                surf.blit(card_img, (20, 30))
            except Exception as e:
                print(f"Error loading image {self.image_filename}: {e}")
                self.draw_card_text(surf)
        else:
            self.draw_card_text(surf)
        
        # Draw card name at bottom
        name_surface = pygame.Surface((CARD_WIDTH - 20, 50), pygame.SRCALPHA)
        pygame.draw.rect(name_surface, (*GOLD, 100), (0, 0, name_surface.get_width(), name_surface.get_height()), border_radius=10)
        name_text = small_font.render(self.name, True, WHITE)
        name_surface.blit(name_text, (name_surface.get_width()//2 - name_text.get_width()//2, 
                                    name_surface.get_height()//2 - name_text.get_height()//2))
        surf.blit(name_surface, (10, CARD_HEIGHT - 60))
        
        return surf
    
    
    
    def draw_card_text(self, surf):
        """Fallback method to draw card name as text when image isn't available"""
        words = self.name.split()
        lines = []
        current_line = words[0]
        for word in words[1:]:
            if len(current_line) + len(word) < 15:
                current_line += " " + word
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
        
        # Render text with larger font and better spacing
        for i, line in enumerate(lines[:4]):  # Now can fit 4 lines
            text = font.render(line, True, WHITE)
            shadow = font.render(line, True, (0, 0, 0, 150))
            
            # Draw shadow first
            surf.blit(shadow, (CARD_WIDTH//2 - text.get_width()//2 + 2, 60 + i*50 + 2))
            # Then draw main text
            surf.blit(text, (CARD_WIDTH//2 - text.get_width()//2, 60 + i*50))






class TarotGame:
    def __init__(self):
        self.deck = full_deck.copy()
        self.drawn_cards = []
        self.current_spread = SPREAD_SINGLE
        self.reading_data = None
        self.current_cards = []
        self.message = "Welcome to Mystic Tarot Reader!"
        self.showing_meaning = False
        self.selected_card = None
        self.time = 0
        self.button_hover = None
        self.crystal_ball_img = None
        self.ai_response = None
        self.showing_ai_response = False
        
        self.spread_positions = {
            SPREAD_SINGLE: [(WIDTH//2, HEIGHT//2 - 100)],
            SPREAD_THREE: [
                (WIDTH//4, HEIGHT//2 - 100), 
                (WIDTH//2, HEIGHT//2 - 100), 
                (3*WIDTH//4, HEIGHT//2 - 100)
            ],
            SPREAD_CELTIC: [
                (WIDTH//2, HEIGHT//3),                    # 1 - Present (center top)
                (WIDTH//2, 2*HEIGHT//3),                 # 2 - Challenge (center bottom)
                (WIDTH//4, HEIGHT//3 - CARD_HEIGHT//2),  # 3 - Past (left of 1, moved up)
                (3*WIDTH//4, HEIGHT//3 - CARD_HEIGHT//2),# 4 - Future (right of 1, moved up)
                (WIDTH//4, HEIGHT//2),                   # 5 - Above (left middle)
                (3*WIDTH//4, HEIGHT//2),                 # 6 - Below (right middle)
                (WIDTH//4, 2*HEIGHT//3 + CARD_HEIGHT//2),# 7 - Advice (left bottom, moved down)
                (3*WIDTH//4, 2*HEIGHT//3 + CARD_HEIGHT//2), # 8 - External (right bottom, moved down)
                (WIDTH//6, HEIGHT//2),                   # 9 - Hopes/Fears (far left)
                (5*WIDTH//6, HEIGHT//2)                  # 10 - Outcome (far right)
            ]
        }
        self.spread_names = {
            SPREAD_SINGLE: ["Current Situation"],
            SPREAD_THREE: ["Past", "Present", "Future"],
            SPREAD_CELTIC: [
                "1 - Present", "2 - Challenge", "3 - Past", "4 - Future",
                "5 - Above", "6 - Below", "7 - Advice", "8 - External",
                "9 - Hopes/Fears", "10 - Outcome"
            ]
        }
        # Try to load crystal ball image
        try:
            self.crystal_ball_img = pygame.image.load("crystal_ball.png")
            self.crystal_ball_img = pygame.transform.scale(self.crystal_ball_img, (200, 200))
        except:
            self.crystal_ball_img = None


    def get_ai_reading(self):
        """Send the current reading to OpenAI and get a mystical interpretation"""
        if not self.current_cards:
            self.message = "No reading to interpret! Draw cards first."
            return False
        
        try:
            # Prepare the reading data for the AI
            reading_data = self.get_reading_data()
            if not reading_data:
                self.message = "Could not prepare reading data."
                return False
            
            # Format the prompt
            prompt = (
                f"Act as a mystical tarot card reader. Interpret this {reading_data['spread_type']} spread:\n\n"
            )
            
            for card in reading_data['cards']:
                prompt += (
                    f"Position: {card['position']}\n"
                    f"Card: {card['card_name']} ({'Reversed' if card['reversed'] else 'Upright'})\n"
                    f"Meaning: {card['meaning']}\n\n"
                )
            
            prompt += (
                "\n\n"
                "||| STRICT FORMATTING COMMANDS |||\n\n"
                "1. **MANDATORY SPACING FORMAT**:\n"
                "[NEWLINE][NEWLINE]\n"
                "[EMOJI] [Position#] - [Position Name]: [Card Name] (Upright/Reversed)[NEWLINE]\n"
                "[Interpretation paragraph 1][NEWLINE]\n"
                "[Interpretation paragraph 2][NEWLINE]\n"
                "[NEWLINE]\n\n"
                "2. **INTERPRETATION STRUCTURE**:\n"
                "- First line: Core meaning (complete sentence)\n"
                "- Second line: Practical implications\n"
                "- Third line: Intuitive message\n"
                "- Fourth line: Connection to other cards\n\n"
                "3. **FINAL REFLECTION FORMAT**:\n"
                "[NEWLINE][NEWLINE]\n"
                "🔮 Final Reflection:[NEWLINE]\n"
                "[Paragraph 1][NEWLINE]\n"
                "[Paragraph 2][NEWLINE]\n"
                "[Closing statement][NEWLINE]\n"
                "[NEWLINE]\n\n"
                
                "and return the output in bullet points as below:\n\n"
                "=== EXAMPLE OF REQUIRED OUTPUT ===\n\n"
                "🌟 1 - Present: 4 of Wands (Reversed)\n"
                "You're in a phase where what should feel stable or celebratory—like home, relationships, or creative achievements—feels instead disrupted. This card reversed speaks of conflict within a familiar structure, perhaps tension in a home, team, or partnership. You may be transitioning away from what once brought you comfort, or feeling unsupported as you try to move forward.\n\n"
                "⚔️ 2 - Challenge: 2 of Cups (Reversed)\n"
                "Your biggest challenge right now is a breakdown in communication or emotional connection with someone important. A partnership or relationship is out of balance—maybe romantic, maybe a close friend or ally. Mistrust or misunderstandings may be at play, and healing this rift could be central to your current struggle.\n\n"
                "⏳ 3 - Past: 6 of Cups (Reversed)\n"
                "You've recently been forced to let go of the past—perhaps a memory, old pattern, or nostalgia was holding you back. Whether it was comforting or painful, you’re now in the process of moving forward. This is a sign of emotional growth, though not without discomfort.\n\n"
                "🌑 4 - Future: The Moon (Upright)\n"
                "What’s coming next may feel uncertain or disorienting. The Moon brings confusion, illusions, and hidden truths—things are not what they appear. You will need to rely on intuition, dreams, and your inner compass to navigate what lies ahead. Don't act on fear or illusion—seek clarity in the fog.\n\n"
                "☁️ 5 - Above (Conscious Goal): 6 of Wands (Reversed)\n"
                "You're struggling with recognition and validation. You might feel that your efforts go unnoticed, or you fear failure and public judgment. This card can also point to ego wounds—perhaps you want to win or be seen, but fear losing face. It’s a reminder that true success comes from within, not applause.\n\n"
                "🧑‍🤝‍🧑 6 - Below (Unconscious Influence): 3 of Cups (Upright)\n"
                "At a deeper level, you crave connection, joy, and genuine friendship. There's a strong desire to belong and be celebrated with others—even if recent events have made you feel isolated. This unconscious influence may be guiding you to seek a new sense of community or re-establish joyful bonds.\n\n"
                "🌀 7 - Advice: The World (Reversed)\n"
                "You're being asked to complete what you’ve left unfinished. There’s a cycle in your life—emotional, spiritual, or literal—that hasn’t come to full closure. Fear of change, fear of endings, or feeling like something’s missing is blocking your progress. It’s time to gather your strength and see the journey through.\n\n"
                "💨 8 - External Influences: Knight of Swords (Upright)\n"
                "Your environment is fast-moving and intense, with people or events pushing you toward rapid decisions. Someone around you may be aggressive in their opinions or rushing things. Be wary of impulsive actions—both your own and others'. Stay grounded as you navigate this external pressure.\n\n"
                "💖 9 - Hopes/Fears: 10 of Cups (Upright)\n"
                "At your core, you long for peace, harmony, and emotional fulfillment, particularly within your home or family life. This card speaks to the dream of deep connection, support, and love. But since this is also in your fears, perhaps you’re afraid it may never come—or that you’ll sabotage it. It’s a beautiful vision, but you may fear it's just out of reach.\n\n"
                "🌱 10 - Outcome: 7 of Pentacles (Upright)\n"
                "Your outcome suggests growth, but not overnight. This is a card of patient progress—planting seeds and watching them slowly bear fruit. Your effort will pay off, but only if you assess your investments wisely. This may not be a dramatic resolution, but it’s a solid one: a future earned through care, consistency, and self-evaluation.\n\n"
                "🔮 Final Reflection:\n"
                "This spread tells the story of someone in emotional transition—between letting go of the past, confronting a broken bond or relationship, and walking a foggy, uncertain path forward. You're being invited to face illusions, finish old cycles, and trust your intuition. While it may feel like support is lacking now, the foundation for lasting growth, healing, and joyful connection is already within reach—you just have to be willing to do the patient work, and close what needs closing.\n\n"
                "The cards encourage you to face these challenges directly...\n"
                "Remember: Growth often comes through discomfort.\n"
            )

            
            # Updated OpenAI API call
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a wise, mystical tarot reader with deep intuitive powers. Provide insightful, poetic interpretations of tarot readings."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            self.ai_response = response.choices[0].message.content
            self.showing_ai_response = True
            self.message = "Received mystical interpretation from the AI."
            return True
            
        except Exception as e:
            self.message = f"Failed to get AI reading: {str(e)}"
            return False






    def reset_deck(self):
        """Completely reset the deck to full 78 cards and shuffle"""
        self.deck = full_deck.copy()  # Restore all 78 cards
        self.drawn_cards = []  # Clear drawn cards history
        random.shuffle(self.deck)  # Shuffle the fresh deck
        self.message = "Deck has been reset to 78 cards and shuffled."

    def shuffle_deck(self):
        """Reset to full 78-card deck, clear current reading, and shuffle"""
        self.deck = full_deck.copy()
        self.drawn_cards = []
        self.current_cards = []  # Clear any displayed cards
        random.shuffle(self.deck)
        self.message = "Deck reset to 78 cards and shuffled. Current reading cleared."
        self.showing_meaning = False  # Hide any card meaning being shown
        self.selected_card = None  # Deselect any selected card

    def draw_card(self):
        if not self.deck:
            self.reset_deck()
            
        card_name = self.deck.pop()
        card = TarotCard(card_name)
        self.drawn_cards.append(card)
        return card

    def do_spread(self, spread_type):
        self.current_spread = spread_type
        self.current_cards = []
        positions = self.spread_positions[spread_type]
        
        # Always reset and shuffle the deck before each new reading
        self.reset_deck()
        
        for _ in range(len(positions)):
            self.current_cards.append(self.draw_card())
        
        self.message = f"Drew {len(positions)} cards for {self.get_spread_name(spread_type)} spread."

    def get_spread_name(self, spread_type):
        if spread_type == SPREAD_SINGLE:
            return "Single Card"
        elif spread_type == SPREAD_THREE:
            return "Past-Present-Future"
        else:
            return "Celtic Cross"





    def draw(self, screen):
        # Draw background
        screen.blit(background, (0, 0))
        

        
        # Draw title with fancy effects
        title_text = title_font.render("Mystic Tarot Reader", True, WHITE)
        shadow_text = title_font.render("Mystic Tarot Reader", True, (0, 0, 0, 150))
        
        # Create a glowing effect behind the title
        title_glow = pygame.Surface((title_text.get_width() + 40, title_text.get_height() + 40), pygame.SRCALPHA)
        glow_radius = 20 + 5 * math.sin(self.time * 2)
        for r in range(int(glow_radius), 0, -1):
            alpha = int(50 * (r / glow_radius))
            pygame.draw.rect(title_glow, (*LIGHT_PURPLE, alpha), 
                            (20 - r, 20 - r, title_text.get_width() + 2*r, title_text.get_height() + 2*r), 
                            border_radius=10)
        
        screen.blit(title_glow, (WIDTH//2 - title_glow.get_width()//2, 20))
        screen.blit(shadow_text, (WIDTH//2 - title_text.get_width()//2 + 3, 40 + 3))
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 40))
        
        # Draw deck status with crystal ball icon
        deck_status = small_font.render(f"Cards left: {len(self.deck)}", True, WHITE)
        if self.crystal_ball_img:
            crystal_ball_glow = pygame.Surface((self.crystal_ball_img.get_width(), 
                                                self.crystal_ball_img.get_height()), pygame.SRCALPHA)
            glow_alpha = 50 + int(50 * math.sin(self.time * 3))
            crystal_ball_glow.fill((*LIGHT_PURPLE, glow_alpha))
            screen.blit(crystal_ball_glow, (30 - 10, 30 - 10), special_flags=pygame.BLEND_ADD)
            screen.blit(self.crystal_ball_img, (30, 30))
            screen.blit(deck_status, (30 + self.crystal_ball_img.get_width() + 15, 
                                    30 + self.crystal_ball_img.get_height()//2 - deck_status.get_height()//2))
        else:
            screen.blit(deck_status, (30, 30))
        
        # Draw message with parchment background
        if self.message:
            msg_width = font.size(self.message)[0] + 40
            msg_height = 50
            msg_surface = pygame.Surface((msg_width, msg_height), pygame.SRCALPHA)
            
            # Create parchment-like background
            msg_surface.fill((220, 210, 180, 200))
            pygame.draw.rect(msg_surface, (180, 160, 120, 255), (0, 0, msg_width, msg_height), 3)
            

            
            msg_text = font.render(self.message, True, DARK_PURPLE)
            msg_surface.blit(msg_text, (msg_width//2 - msg_text.get_width()//2, 
                                        msg_height//2 - msg_text.get_height()//2))
            
            screen.blit(msg_surface, (WIDTH//2 - msg_width//2, 120))
        
        # Draw buttons with fancy hover effects
        button_y = HEIGHT - 120
        button_width = 200
        button_height = 70
        button_spacing = 220
        
        buttons = [
            ("Shuffle", 0, self.shuffle_deck),
            ("Single Card", 1, lambda: self.do_spread(SPREAD_SINGLE)),
            ("3-Card Spread", 2, lambda: self.do_spread(SPREAD_THREE)),
            ("Celtic Cross", 3, lambda: self.do_spread(SPREAD_CELTIC)),
            ("Save Reading", 4, self.save_reading_to_json),
            ("AI Reading", 5, self.get_ai_reading)
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        self.button_hover = None
        
        for i, (text, pos, action) in enumerate(buttons):
            button_x = WIDTH//2 - (button_spacing * len(buttons))//2 + pos * button_spacing
            
            # Check hover state
            hover = (button_x <= mouse_pos[0] <= button_x + button_width and 
                    button_y <= mouse_pos[1] <= button_y + button_height)
            
            if hover:
                self.button_hover = i
            
            # Draw button with hover effects
            button_surf = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
            
            if hover:
                # Hover state - glowing button
                for r in range(15, 0, -1):
                    alpha = 50 - r * 3
                    pygame.draw.rect(button_surf, (*GOLD, alpha), 
                                    (button_width//2 - r*10, button_height//2 - r*5, r*20, r*10), 
                                    border_radius=10)
                
                pygame.draw.rect(button_surf, GOLD, (0, 0, button_width, button_height), 3, border_radius=10)
                button_surf.fill((*GOLD, 20), special_flags=pygame.BLEND_ADD)
            else:
                # Normal state
                pygame.draw.rect(button_surf, (*PURPLE, 180), (0, 0, button_width, button_height), 0, border_radius=10)
                pygame.draw.rect(button_surf, GOLD, (0, 0, button_width, button_height), 3, border_radius=10)
            
            # Draw button text
            text_surf = small_font.render(text, True, WHITE)
            shadow_surf = small_font.render(text, True, (0, 0, 0, 150))
            
            button_surf.blit(shadow_surf, (button_width//2 - text_surf.get_width()//2 + 2, 
                                            button_height//2 - text_surf.get_height()//2 + 2))
            button_surf.blit(text_surf, (button_width//2 - text_surf.get_width()//2, 
                                        button_height//2 - text_surf.get_height()//2))
            
            screen.blit(button_surf, (button_x, button_y))
        
        # Draw current cards with animations
        if self.current_cards:
            positions = self.spread_positions[self.current_spread]
            names = self.spread_names[self.current_spread]
            
            for i, (card, pos) in enumerate(zip(self.current_cards, positions)):
                # Update card animations
                card.update()
                
                # Draw card with glow effect if selected
                x, y = pos
                if card == self.selected_card:
                    # Create a pulsing glow effect
                    glow_intensity = 0.5 + 0.5 * math.sin(card.glow_phase)
                    glow_surf = pygame.Surface((CARD_WIDTH + 40, CARD_HEIGHT + 40), pygame.SRCALPHA)
                    for r in range(20, 0, -1):
                        alpha = int(50 * glow_intensity * (r / 20))
                        pygame.draw.rect(glow_surf, (*GOLD, alpha), 
                                        (20 - r, 20 - r, CARD_WIDTH + 2*r, CARD_HEIGHT + 2*r), 
                                        border_radius=15)
                    screen.blit(glow_surf, (x - CARD_WIDTH//2 - 20, y - CARD_HEIGHT//2 - 20))
                
                # Draw card with subtle shadow
                shadow_offset = 10
                shadow_surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
                shadow_surf.fill((0, 0, 0, 100))
                screen.blit(shadow_surf, (x - CARD_WIDTH//2 + shadow_offset, y - CARD_HEIGHT//2 + shadow_offset))
                
                # Draw the actual card with slight hover effect
                hover_effect = 0
                if (x - CARD_WIDTH//2 <= mouse_pos[0] <= x + CARD_WIDTH//2 and 
                    y - CARD_HEIGHT//2 <= mouse_pos[1] <= y + CARD_HEIGHT//2):
                    hover_effect = -10 * math.sin(self.time * 5)
                
                screen.blit(card.image, (x - CARD_WIDTH//2, y - CARD_HEIGHT//2 + hover_effect))
                
                # Draw position name with fancy styling
                name_bg = pygame.Surface((200, 40), pygame.SRCALPHA)
                pygame.draw.rect(name_bg, (*DARK_PURPLE, 200), (0, 0, 200, 40), border_radius=10)
                pygame.draw.rect(name_bg, GOLD, (0, 0, 200, 40), 2, border_radius=10)
                
                name_text = small_font.render(names[i], True, WHITE)
                name_bg.blit(name_text, (100 - name_text.get_width()//2, 20 - name_text.get_height()//2))
                
                screen.blit(name_bg, (x - 100, y + CARD_HEIGHT//2 + 20))
                
                if card.reversed:
                    rev_text = small_font.render("(Reversed)", True, (255, 100, 100))
                    rev_bg = pygame.Surface((rev_text.get_width() + 20, rev_text.get_height() + 10), pygame.SRCALPHA)
                    pygame.draw.rect(rev_bg, (*DARK_PURPLE, 200), (0, 0, rev_bg.get_width(), rev_bg.get_height()), border_radius=5)
                    rev_bg.blit(rev_text, (10, 5))
                    screen.blit(rev_bg, (x - rev_bg.get_width()//2, y + CARD_HEIGHT//2 + 70))
        
        # Draw meaning if showing
        if self.showing_meaning and self.selected_card:
            self.draw_meaning_box(screen)


        # Draw AI response if showing
        if self.showing_ai_response:
            if self.draw_ai_response_box(screen):
                self.showing_ai_response = False







    def draw_ai_response_box(self, screen):
        """Draw the AI interpretation in a fancy box with proper section breaks"""
        if not self.ai_response:
            return False
            
        # Box dimensions
        box_width = min(1500, WIDTH - 100)
        box_height = min(1500, HEIGHT - 200)
        box_x = (WIDTH - box_width) // 2
        box_y = (HEIGHT - box_height) // 2
        
        # Create ornate background
        box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        
        # Main parchment background with gradient
        for y in range(box_height):
            ratio = y / box_height
            r = int(240 - 30 * ratio)
            g = int(230 - 40 * ratio)
            b = int(210 - 30 * ratio)
            pygame.draw.line(box_surf, (r, g, b, 240), (0, y), (box_width, y))
        
        # Add decorative border
        pygame.draw.rect(box_surf, DARK_GOLD, (0, 0, box_width, box_height), 5, border_radius=15)
        
        # Add mystical symbols in corners
        corner_size = 30
        for x, y in [(0, 0), (box_width, 0), (0, box_height), (box_width, box_height)]:
            if x == 0 and y == 0:  # Top-left - moon symbol
                pygame.draw.circle(box_surf, DARK_GOLD, (corner_size//2, corner_size//2), corner_size//3, 2)
                pygame.draw.arc(box_surf, DARK_GOLD, 
                            (corner_size//6, corner_size//6, 2*corner_size//3, 2*corner_size//3),
                            math.pi/2, 3*math.pi/2, 2)
            elif x == box_width and y == 0:  # Top-right - sun symbol
                pygame.draw.circle(box_surf, DARK_GOLD, (box_width-corner_size//2, corner_size//2), corner_size//3, 2)
                for i in range(8):
                    angle = i * math.pi/4
                    end_x = box_width-corner_size//2 + (corner_size//3 + 5) * math.cos(angle)
                    end_y = corner_size//2 + (corner_size//3 + 5) * math.sin(angle)
                    pygame.draw.line(box_surf, DARK_GOLD,
                                (box_width-corner_size//2, corner_size//2),
                                (end_x, end_y), 2)
        
        # Draw the surface to screen
        screen.blit(box_surf, (box_x, box_y))
        
        # Draw title
        title = title_font.render("Mystical Interpretation", True, DARK_PURPLE)
        screen.blit(title, (box_x + box_width//2 - title.get_width()//2, box_y + 20))
        
        # Process and render text with emoji breaks
        emoji_list = ["🌟", "⚔️", "⏳", "🌑", "☁️", "🧑‍🤝‍🧑", "🌀", "💨", "💖", "🌱", "🔮"]
        sections = []
        current_section = ""
        
        # Split text at emojis while keeping them
        for char in self.ai_response:
            if char in emoji_list:
                if current_section:
                    sections.append(current_section)
                    current_section = ""
            current_section += char
        if current_section:
            sections.append(current_section)
        
        # Render each section with proper spacing
        line_height = 30
        max_lines = (box_height - 100) // line_height
        current_y = box_y + 80
        lines_rendered = 0
        
        for section in sections:
            # Skip empty sections
            if not section.strip():
                continue
                
            # Split section into words
            words = section.split()
            current_line = ""
            
            # Word wrapping logic
            for word in words:
                test_line = current_line + word + " "
                if font.size(test_line)[0] < box_width - 40:
                    current_line = test_line
                else:
                    if lines_rendered >= max_lines:
                        break
                    text = font.render(current_line, True, DARK_PURPLE)
                    screen.blit(text, (box_x + 20, current_y))
                    current_y += line_height
                    lines_rendered += 1
                    current_line = word + " "
            
            # Render remaining words
            if current_line and lines_rendered < max_lines:
                text = font.render(current_line, True, DARK_PURPLE)
                screen.blit(text, (box_x + 20, current_y))
                current_y += line_height
                lines_rendered += 1
            
            # Add extra space between sections
            if lines_rendered < max_lines and section != sections[-1]:
                current_y += line_height // 2  # Half-line spacing
                lines_rendered += 0.5
        
        # Draw close button
        close_button_y = box_y + box_height - 60
        close_button_x = box_x + box_width//2 - 100
        
        # Check hover state
        mouse_pos = pygame.mouse.get_pos()
        hover = (close_button_x <= mouse_pos[0] <= close_button_x + 200 and 
                close_button_y <= mouse_pos[1] <= close_button_y + 50)
        
        # Draw button
        close_surf = pygame.Surface((200, 50), pygame.SRCALPHA)
        if hover:
            pygame.draw.rect(close_surf, (*PURPLE, 150), (0, 0, 200, 50), 0, border_radius=10)
            pygame.draw.rect(close_surf, GOLD, (0, 0, 200, 50), 3, border_radius=10)
        else:
            pygame.draw.rect(close_surf, (*PURPLE, 100), (0, 0, 200, 50), 0, border_radius=10)
            pygame.draw.rect(close_surf, GOLD, (0, 0, 200, 50), 2, border_radius=10)
        
        close_text = small_font.render("Close", True, WHITE)
        close_surf.blit(close_text, (100 - close_text.get_width()//2, 
                                25 - close_text.get_height()//2))
        
        screen.blit(close_surf, (close_button_x, close_button_y))
        
        # Return True if close button is hovered and clicked
        return hover and pygame.mouse.get_pressed()[0]








    def draw_meaning_box(self, screen):
        if not self.current_cards:
            return
            
        # Calculate dimensions and position for bottom placement
        box_width = min(2000, WIDTH - 40)  # Max width with some margin
        box_height = min(1000, HEIGHT - 100)  # Increased height to accommodate multiple cards
        box_x = (WIDTH - box_width) // 2
        box_y = HEIGHT - box_height - 100  # Position at bottom with 30px margin
        
        # Create ornate background
        box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        
        # Main parchment background
        box_surf.fill((240, 230, 210, 240))
        
        # Add decorative border
        pygame.draw.rect(box_surf, DARK_GOLD, (0, 0, box_width, box_height), 5, border_radius=15)
        
        # Add corner decorations
        corner_size = 30
        for x, y in [(0, 0), (box_width, 0), (0, box_height), (box_width, box_height)]:
            if x == 0 and y == 0:  # Top-left
                points = [(5, 5), (corner_size, 5), (5, corner_size)]
            elif x == box_width and y == 0:  # Top-right
                points = [(box_width-5, 5), (box_width-corner_size, 5), (box_width-5, corner_size)]
            elif x == 0 and y == box_height:  # Bottom-left
                points = [(5, box_height-5), (corner_size, box_height-5), (5, box_height-corner_size)]
            else:  # Bottom-right
                points = [(box_width-5, box_height-5), (box_width-corner_size, box_height-5), 
                        (box_width-5, box_height-corner_size)]
            pygame.draw.polygon(box_surf, DARK_GOLD, points)
        
        # Draw the surface to screen
        screen.blit(box_surf, (box_x, box_y))
        
        # Draw spread title
        spread_title = title_font.render(f"{self.get_spread_name(self.current_spread)} Reading", True, DARK_PURPLE)
        screen.blit(spread_title, (box_x + box_width//2 - spread_title.get_width()//2, box_y + 20))
        
        # Calculate layout based on number of cards
        num_cards = len(self.current_cards)
        card_spacing = 20
        section_height = box_height - 100  # Leave space for title and close button
        
        if num_cards == 1:
            # Single card - full width meaning
            self.draw_card_meaning(screen, self.current_cards[0], 
                                box_x + 20, box_y + 80, 
                                box_width - 40, section_height - 20)
        elif num_cards == 3:
            # 3 cards - divide into 3 columns
            col_width = (box_width - 40 - 2 * card_spacing) // 3
            for i, card in enumerate(self.current_cards):
                x = box_x + 20 + i * (col_width + card_spacing)
                self.draw_card_meaning(screen, card, 
                                    x, box_y + 80, 
                                    col_width, section_height - 20,
                                    include_name=True)
        elif num_cards == 10:
            # Celtic Cross - 2 rows of 5 columns
            col_width = (box_width - 40 - 4 * card_spacing) // 5
            row_height = section_height // 2 - 10
            
            # First row (positions 1-5)
            for i in range(5):
                x = box_x + 20 + i * (col_width + card_spacing)
                self.draw_card_meaning(screen, self.current_cards[i], 
                                    x, box_y + 80, 
                                    col_width, row_height,
                                    include_name=True)
            
            # Second row (positions 6-10)
            for i in range(5, 10):
                x = box_x + 20 + (i-5) * (col_width + card_spacing)
                self.draw_card_meaning(screen, self.current_cards[i], 
                                    x, box_y + 80 + row_height + 10, 
                                    col_width, row_height,
                                    include_name=True)
        else:
            # Fallback for other spread sizes
            y_offset = 80
            for card in self.current_cards:
                self.draw_card_meaning(screen, card, 
                                    box_x + 20, box_y + y_offset, 
                                    box_width - 40, 100,
                                    include_name=True)
                y_offset += 120
        
        # Draw close button at bottom of the box
        close_button_y = box_y + box_height - 70
        close_button_x = box_x + box_width//2 - 100
        
        # Check hover state
        mouse_pos = pygame.mouse.get_pos()
        hover = (close_button_x <= mouse_pos[0] <= close_button_x + 200 and 
                close_button_y <= mouse_pos[1] <= close_button_y + 60)
        
        # Draw button with hover effect
        close_surf = pygame.Surface((200, 60), pygame.SRCALPHA)
        
        if hover:
            # Hover state - glowing
            for r in range(10, 0, -1):
                alpha = 50 - r * 5
                pygame.draw.rect(close_surf, (*PURPLE, alpha), 
                            (100 - r*10, 30 - r*5, r*20, r*10), 
                            border_radius=10)
            
            pygame.draw.rect(close_surf, PURPLE, (0, 0, 200, 60), 3, border_radius=10)
            close_surf.fill((*PURPLE, 20), special_flags=pygame.BLEND_ADD)
        else:
            # Normal state
            pygame.draw.rect(close_surf, (*PURPLE, 180), (0, 0, 200, 60), 0, border_radius=10)
            pygame.draw.rect(close_surf, GOLD, (0, 0, 200, 60), 3, border_radius=10)
        
        # Draw button text (without shadow)
        close_text = font.render("Close Reading", True, WHITE)
        close_surf.blit(close_text, (100 - close_text.get_width()//2, 
                                30 - close_text.get_height()//2))
        
        screen.blit(close_surf, (close_button_x, close_button_y))
        
        # Return True if close button is hovered and clicked
        return hover and pygame.mouse.get_pressed()[0]




    def draw_card_meaning(self, screen, card, x, y, width, height, include_name=False):
        """Helper method to draw a single card's meaning in a specified area"""
        # Draw card name if requested
        current_y = y
        
        if include_name:
            name_text = small_font.render(card.name, True, DARK_PURPLE)
            screen.blit(name_text, (x + width//2 - name_text.get_width()//2, current_y))
            current_y += 30
            
            if card.reversed:
                rev_text = small_font.render("(Reversed)", True, (200, 50, 50))
                screen.blit(rev_text, (x + width//2 - rev_text.get_width()//2, current_y))
                current_y += 30
        
        # Get the meaning
        meaning = card.reversed_meaning if card.reversed else card.upright
        
        # Render wrapped text
        words = meaning.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if meaning_font.size(test_line)[0] < width - 20:  # Account for margins
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        
        # Draw wrapped text lines
        for i, line in enumerate(lines):
            if current_y + i*35 > y + height:  # Don't overflow the allocated space
                break
            
            text = meaning_font.render(line, True, DARK_PURPLE)
            screen.blit(text, (x + 10, current_y + i*35))






    def handle_click(self, pos):
        x, y = pos
        
        # Closes the AI response
        if self.showing_ai_response:
            self.showing_ai_response = False
            return
        
        # Check if clicked on a card
        if self.current_cards:
            positions = self.spread_positions[self.current_spread]
            for i, card_pos in enumerate(positions):
                px, py = card_pos
                if (px - CARD_WIDTH//2 < x < px + CARD_WIDTH//2 and 
                    py - CARD_HEIGHT//2 < y < py + CARD_HEIGHT//2):
                    self.selected_card = self.current_cards[i]
                    self.showing_meaning = True
                    return
        
        # Check if clicked on the close button in meaning box
        if self.showing_meaning and self.selected_card:
            if self.draw_meaning_box(screen):
                self.showing_meaning = False
                return
        
        # Check buttons - must match EXACTLY how they're drawn in draw()
        button_y = HEIGHT - 120
        button_width = 200
        button_height = 70
        button_spacing = 220
        
        # This must match the buttons list in draw() exactly
        buttons = [
            ("Shuffle", 0, self.shuffle_deck),
            ("Single Card", 1, lambda: self.do_spread(SPREAD_SINGLE)),
            ("3-Card Spread", 2, lambda: self.do_spread(SPREAD_THREE)),
            ("Celtic Cross", 3, lambda: self.do_spread(SPREAD_CELTIC)),
            ("Save Reading", 4, self.save_reading_to_json),
            ("AI Reading", 5, self.get_ai_reading)
        ]
        
        # Calculate total width of all buttons with spacing
        total_width = (len(buttons)-1) * button_spacing + button_width
        start_x = WIDTH//2 - total_width//2
        
        for i, (text, pos, action) in enumerate(buttons):
            button_x = start_x + i * button_spacing
            if (button_x <= x <= button_x + button_width and 
                button_y <= y <= button_y + button_height):
                action()
                return






    def save_reading_to_json(self):
        """Save the current reading to a JSON file"""
        if not self.current_cards:
            self.message = "No reading to save!"
            return False
        
        try:
            # Create a 'readings' directory if it doesn't exist
            if not os.path.exists('readings'):
                os.makedirs('readings')
            
            # Generate a timestamped filename
            filename = f"readings/tarot_reading.json"
            
            # Get the current reading data
            self.reading_data = self.get_reading_data()
            
            # Save to file
            with open(filename, 'w') as f:
                json.dump(self.reading_data, f, indent=2)
            
            self.message = f"Reading saved as {filename}"
            return True
        except Exception as e:
            self.message = f"Failed to save reading: {str(e)}"
            return False






    def get_reading_data(self):
        """Return just the card positions and card data for the current reading"""
        if not self.current_cards:
            return None
            
        reading = {
            "spread_type": self.get_spread_name(self.current_spread),
            "cards": []
        }
        
        positions = self.spread_names[self.current_spread]
        
        for i, card in enumerate(self.current_cards):
            card_data = {
                "position": positions[i],
                "card_name": card.name,
                "reversed": card.reversed,
                "meaning": card.reversed_meaning if card.reversed else card.upright
            }
            reading["cards"].append(card_data)
        
        return reading






def main():
    clock = pygame.time.Clock()
    game = TarotGame()
    game.reset_deck()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.handle_click(event.pos)
        
        game.draw(screen)
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    sys.exit()




if __name__ == "__main__":
    main()
