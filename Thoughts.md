# Thoughts during development

## Initial thoughts

- After reading the pdf of the game, I didn't want to dive right into it. I wanted to thoroughly think about the different components 
for a unqiue game that I wanted to create.

## Gameplay
- I started by asking myself:
  - How do I want the game played?
  - Do I just want it to be a single player mode or be able to include
    multiple people?
  - Should there be different difficulty levels?
  - Should I put a limit to the amount of players that are playing?
  - What happens when someone inputs the wrong message?
  - Does the game just end when I win or lose?
  - How am I going to track the location of a number that's correct and count the number of numbers that are correct?
  - If there's a multiplayer mode should the players be able to choose if they want to have the same random sequence as the others
  or should it be unique to each player?
  - For Hints I had several questions:
    - How do I want the hints to work? 
    - Should I give them unlimited hints or limit it to a certain number?
    - How should the hint even work?
    - Should I give them a specific location of a number, or just a number thats in the sequence with no location?
    - Should a hint count as a "turn" and remove an attempt from your current guess count?
  - For multiplayer mode I had several questions:
    - How should I keep track of who is winning?
    - If they are playing the multiplayer mode and choose to have a shared random number sequence how will the winner be decided?
      - Should I assume that the other players will not see the sequence that won by the prior player?
      - Playing in the cli players might see the correct answer and cheat.
    - If at the end of the game there were players who didn't figure out the sequence should I just rank them last together?
  - What messages did I want the player to see on the screen as they played?
  - 

## Code Design
- When thinking about the design of the game in the code, I was really curious as to what I could potentially need.
- A file for 
  - constants,
  - cli,
  - the api (random.org api),
  - game logic,
  - potentially a formatting file? (Keep wording consistent and easy to tweak without hunting through logic files),
  - models (gameConfig, player, and potentially more)
  - guess tracker (Correct locations / correct numbers computed here for each attempt. will return it back to the game so it doesn't save anything here)
  - ReadMe doc of course
  
