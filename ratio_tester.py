from moviecell import MovieCell


def get_moviecells(n: int) -> list[MovieCell]:
    return [MovieCell(
        title='The Fifth Element',
        director='Jeff Green',
        rating=3.5,
        im_path='images/The-Fifth-Element.png'
    ) for _ in range(n)]