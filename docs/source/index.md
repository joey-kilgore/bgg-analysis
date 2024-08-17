(heading-target)=
# BGG Analysis

Currently, 5 members of our game group have posted their BGG username to provide analysis.

They are:
- [mrjoeboo123](https://boardgamegeek.com/collection/user/mrjoeboo123)
- [Schwingzilla](https://boardgamegeek.com/collection/user/Schwingzilla)
- [ngeagan](https://boardgamegeek.com/collection/user/ngeagan)
- [Wellsroderick](https://boardgamegeek.com/collection/user/Wellsroderick)
- [withouthavingseen](https://boardgamegeek.com/collection/user/withouthavingseen)

and checkout the [github repo](https://github.com/joey-kilgore/bgg-analysis)

## Overview of collections

Based on the BGG stats we can first get an overview of everyone's collections. 
See the `gameGroupAnalysis.ipynb` jupyter notebook for the code.

```{include} generated/overview.md
```


## Ratings

The next piece of data we can grab is everyone's game ratings

![mrjoeboo123 ratings](/plots/mrjoeboo123.png)
![Schwingzilla ratings](/plots/Schwingzilla.png)
![ngeagan ratings](/plots/ngeagan.png)
![Wellsroderick ratings](/plots/Wellsroderick.png)
![withouthavingseen ratings](/plots/withouthavingseen.png)

## Common Interests

We can take the ratings that everyone has and find games where 2 or more people rate that game above an 8.  

```{include} generated/common_interests.html
```

## Wish and Own  
This is a list of games that one player wants to play (listed as a wishlist item)
and another player owns that game.

```{include} generated/wish_own.html
```

## Common Owns
Games that 2 or more people own.

```{include} generated/multi_own.html
```

