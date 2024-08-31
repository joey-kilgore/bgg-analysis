(heading-target)=
# BGG Analysis

Currently, 5 members of our game group have posted their BGG username to provide analysis.

They are:
- [joeyLiu](https://boardgamegeek.com/collection/user/joeyLiu)
- [Schwingzilla](https://boardgamegeek.com/collection/user/Schwingzilla)
- [ngeagan](https://boardgamegeek.com/collection/user/ngeagan)
- [Wellsroderick](https://boardgamegeek.com/collection/user/Wellsroderick)
- [withouthavingseen](https://boardgamegeek.com/collection/user/withouthavingseen)
- [jackieh9](https://boardgamegeek.com/collection/user/jackieh9)
- [mcrump](https://boardgamegeek.com/collection/user/mcrump)

and checkout the [github repo](https://github.com/joey-kilgore/bgg-analysis)

## Overview of collections

To search collections checkout the [search page](./own_search.md)

Based on the BGG stats we can first get an overview of everyone's collections. 
See the `gameGroupAnalysis.ipynb` jupyter notebook for the code.

```{include} _static/overview.md
```


## Ratings

The next piece of data we can grab is everyone's game ratings

![joeyLiu ratings](/plots/joeyLiu.png)
![Schwingzilla ratings](/plots/Schwingzilla.png)
![ngeagan ratings](/plots/ngeagan.png)
![Wellsroderick ratings](/plots/Wellsroderick.png)
![withouthavingseen ratings](/plots/withouthavingseen.png)
![jackieh9 ratings](/plots/jackieh9.png)
![mcrump ratings](/plots/mcrump.png)

## Common Interests
TLDR - We compare peoples ratings, and take games where both people give it a relatively high rating compared to other games.

Details - We can take the ratings that everyone has and find games where 2 or more people rate that game above their average rating + 1.5 standard devations (rounded down since most people rate whole numbers). This would place games listed here in a users top ~6.5% of game ratings (93.5% would be captured from a gaussian distribution). In practice we capture much more than 6.5% since we round down to the nearest integer value. This value for each player is shown on their histogram above for reference.

```{raw} html
:file: _static/common_interests.html
```

## Wish and Own  
This is a list of games that one player wants to play (listed as a wishlist item)
and another player owns that game.

```{raw} html
:file: _static/wish_own.html
```

## Common Owns
Games that 2 or more people own.

[see graph animation!](_static/own_graph.html)

```{raw} html
:file: _static/multi_own.html
```

```{toctree}
:maxdepth: 2
:caption: Contents:

own_search
