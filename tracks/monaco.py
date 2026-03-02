def create_track():
    from track import Track

    waypoints = [
        # Start/Finish straight (bottom-centre, going right)
        (520, 720), (620, 720), (720, 715),
        # Sainte Devote (tight right-hander)
        (815, 695), (878, 658), (918, 610), (938, 555),
        # Beau Rivage / uphill to Casino
        (933, 495), (916, 436), (890, 382),
        # Massenet / Casino Square
        (855, 337), (796, 313), (730, 305), (665, 312), (606, 332),
        # Mirabeau (right)
        (558, 366), (530, 415), (521, 469), (528, 523),
        # Grand Hotel hairpin (very tight U-turn)
        (546, 572), (572, 613), (606, 643),
        # Portier heading left
        (555, 672), (484, 688), (410, 686),
        # Tunnel exit area
        (338, 670), (270, 646), (211, 608),
        # Nouvelle Chicane
        (166, 554), (149, 490), (163, 429),
        # Tabac
        (202, 378), (256, 343),
        # Swimming Pool section
        (319, 314), (386, 296), (453, 294), (512, 309), (551, 337),
        # Rascasse (slow hairpin)
        (571, 384), (580, 440), (580, 497),
        # Anthony Noghes
        (572, 549), (556, 604), (540, 658),
    ]

    return Track(
        name="Monaco",
        waypoints=waypoints,
        track_width=52,
        bg_color=(45, 65, 95),
        track_color=(82, 82, 90),
        border_color=(205, 205, 205),
        description="Iconic street circuit\nTight and technical",
    )
