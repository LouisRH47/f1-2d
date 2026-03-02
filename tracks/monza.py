def create_track():
    from track import Track

    waypoints = [
        # Pit straight (bottom, going right)
        (195, 655), (375, 648), (565, 638), (755, 626), (935, 613),
        # Prima Variante chicane (right-left)
        (1078, 578), (1113, 518), (1106, 456), (1067, 403),
        # Curva Grande (long fast right-hander)
        (1018, 365), (938, 329), (848, 305), (752, 296),
        # Variante della Roggia (chicane)
        (648, 299), (573, 322), (548, 375), (561, 430),
        # Lesmo 1 & 2
        (607, 468), (648, 500), (636, 543),
        # Lesmo exit
        (597, 566), (538, 570),
        # Ascari chicane
        (468, 554), (403, 526), (372, 470), (383, 414), (415, 370),
        # Back straight going left
        (393, 330), (350, 283), (297, 260),
        # Parabolica (long sweeping right)
        (242, 260), (181, 287), (140, 346), (126, 423),
        (138, 510), (161, 587), (187, 642),
    ]

    return Track(
        name="Monza",
        waypoints=waypoints,
        track_width=72,
        bg_color=(48, 112, 48),
        track_color=(90, 90, 96),
        border_color=(210, 210, 210),
        description="Temple of Speed\nLong straights, fast corners",
    )
