import pygame


##Program to load image 'sky1.png' and crop => save as 'sky2.png'

##Press c to start cropping
##Click first point to crop
##Click second point to crop
##Press enter to confirm crop (Or C to start again)
##Press s to save current image 

def draw_image(image):

    ##Create bounding box (Rectangle) from image
    image_rect = image.get_rect()

    ##Draw image onto window
    window.blit(image, image_rect)

    ##Refresh Screen so image is visable
    pygame.display.flip()

##Used for timing.
clock = pygame.time.Clock()

yellow = (255,253,1)
click_1 = None
click_2 = None


##State 0: Waiting for user the press C key to start crop
##State 1: Waiting for user to click first position to crop from
##State 2: Waiting for user to click second position to crop to
##state 3: Waiting for user to press enter to confirm crop (Pressing C will restart)
state = 0

##Load image to crop
image = pygame.image.load("sky1.png")

##Create a new window with the same dimensions as the image
window = pygame.display.set_mode((image.get_rect().width, image.get_rect().height))

##Draw image onto the window - see fucntion above
draw_image(image)

##Start program loop
running = True
while running:
    ##Refresh display
    pygame.display.flip()
    ##24 frames per second
    clock.tick(24)

    ##If state 2 (Waiting for second mouse press) then draw crop animation (Box)
    if(state == 2):
        ##Draw image again to replace previous drawings
        draw_image(image)

        ##Current mouse position to draw crop box to
        current = pygame.mouse.get_pos()

        ##Draw rectangle from first mouse click to current mouse position

        thickness = 1        
        pygame.draw.rect(window, yellow, (click_1[0], click_1[1], ( current[0] - click_1[0] ) , ( current[1] - click_1[1] )), thickness)

    ##Event handling (user inputs)
    ##pygame.event.get() will get user inputs (mouse clicks, pressing exit) from the computer and 'pass' them to you
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if(event.key == 99): ##C key was pressed
                print("Begin Crop - Click to begin...")
                state = 1
                
            elif(event.key == 13  and state == 3): ##Enter key was pressed (And waiting to confirm crop)
                
                crop_width = click_2[0] - click_1[0]
                crop_height = click_2[1] - click_1[1]
                
                ##Create new 'Surface' - (Blank canvas/ invisable window) to copy cropped image to
                cropped_image = pygame.Surface((crop_width, crop_height))

                ##Copy area of orginal image to make crop
                cropped_image.blit(image, (0,0),  (click_1[0], click_1[1], crop_width, crop_height))
                ##set the current image now
                image = cropped_image

                ##Resize the window
                window = pygame.display.set_mode((crop_width, crop_height))
                ##Redraw image on new window
                draw_image(cropped_image)

                print("Image Cropped - Press s to save...")
                
                state = 0

            elif(event.key == 115 and state == 0): ##S key pressed (And waiting for insructions)
                pygame.image.save(window, 'sky2.png')
                print("Current Image saved as 'sky2.png'")
                
        if event.type == pygame.MOUSEBUTTONUP: ##Mouse pressed
            pos = pygame.mouse.get_pos()
            if(state == 1):
                
                print("1st mouse press")
                click_1 = pos
                state = 2
            
            elif(state == 2):
                print("2nd mouse press - Press Enter to confirm...")
                click_2 = pos
                state = 3

            
        elif event.type == pygame.QUIT: ##User pressed x button, stop and close program
            running = False
            pygame.quit()
