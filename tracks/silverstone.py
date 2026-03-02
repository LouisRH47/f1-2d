def create_track():
    from track import Track

    waypoints = [
        # Pit straight (bottom, going right)
        (320, 720), (480, 720), (640, 715), (800, 710), (940, 690),
        # Copse corner (fast right-hander, going up)
        (1060, 650), (1120, 580), (1130, 500), (1115, 415),
        # Maggotts-Becketts-Chapel esses
        (1070, 355), (990, 320), (900, 305), (825, 285),
        # Hangar straight (going left)
        (740, 255), (640, 235), (530, 220),
        # Stowe corner
        (430, 225), (330, 255), (245, 305), (190, 385),
        # Club / Luffield (going down)
        (170, 475), (180, 570), (225, 650), (305, 710),
    ]

    return Track(
        name="Silverstone",
        waypoints=waypoints,
        track_width=70,
        bg_color=(45, 100, 45),
        track_color=(88, 88, 88),
        border_color=(215, 215, 215),
        description="Classic British GP circuit\nFast sweeping corners",
    )
