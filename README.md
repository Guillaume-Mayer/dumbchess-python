##DumbChess Python is a _didactical_ project

#####I dit it to learn Python.

It's a console chess game with AI.

* It uses a [negamax with alpha-beta pruning algorythm](https://en.wikipedia.org/wiki/Negamax)
* It's very **slow** so it cannot look more than 3, 4 ply ahead
* That results in some stupid moves
* That is why I called it **DumbChess**

I think Python was not the best choice to write such a game, but I learned and that was the point.

To run it :

    python chess.py

The argument in `chess.position.get_best_move` sets the thinking depth.

prof.py is to profile performance, it uses the nice [snakeviz](https://jiffyclub.github.io/snakeviz/) package.

Any comment is welcome...