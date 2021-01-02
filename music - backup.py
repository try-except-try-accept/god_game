import pyxel
from random import choice, randint
from helpers import probability

def split_mel(melody):
    notes = []
    note = ""
    for n in melody:
        note += n
        if n.isdigit():
            notes.append(note)
            note = ""
    return notes

def prep_music():

    n = "c1,c#1,d1,d#1,e1,f1,f#1,g1,g#1,a1,a#1,b1,"
    notes = n + n.replace("1", "2") + n.replace("1", "3") + n.replace("1", "4")
    notes = notes.split(",")
    blues = [0, 3, 5, 6, 7, 10]
    maj = [0, 2, 4, 5, 7, 9, 11]
    min = [0, 2, 3, 5, 7, 8, 10]
    mixy = [0, 4, 5, 7, 11]
    pent = [0, 4, 7, 9]
    spanish = [0, 1, 4, 5, 7, 8, 11]
    all_scales = []

    scales = [blues, maj, min, mixy, pent]
    for intervals in scales:
        all_scales.append(intervals + [i + 12 for i in intervals] + [i + 24 for i in intervals] + [i + 36 for i in intervals])


    for i, scale in enumerate(all_scales):
        print(scale)
        print(notes)
        all_scales[i] = [notes[j] for j in scale]
    print(all_scales)
    scale = choice(all_scales)


    riddims =  [["{0} r  r  r {2} r  r  r"] * 2,
               ["{0}{1} r  r {0}{0} r  r"],
               ["{0} r {1} r {0}{0}{0}{0}"],
               ["{0}{0}{1}{1}{0}{2}{0}{2}"],
               ["{0} r {0} r {1} r  r  r"],
               ["{0} r {0} r {1} r  r  r"],
               ["{0} r {1} r {2} r {0} r"] * 2]

    if probability(50):
        beats = ["c1rrrb4rrr" * 2,
                 "c1rrrb4rrrc1rrc1b4rrr"
                 "c1rrrb4rrrc1rrrb4rrc1",
                 "c1rrrb4rrrc1rrc1b4rc1r",
                 "c1rb4rb4rb4r" * 2]

    else:
        beats = ["c1r r r r r r r a4r r r r r r r ",
                 "c1r r r r r r r a4r g4r f4r r r",
                 "c1 r r rc1r r r a4r r r r r r r",
                 "c1r r r c1r c1r a4r r r r r r r",
                 "c1r r r r r c1r a4r c1r r r r r",
                 "c1r r r r r r r a4r c1a4r a4r r"]

    melodies = []
    for i in range(8):
        melody = ""
        if probability(50):
            root = randint(0, len(scale))
        else:
            root = len(scale) // 2

        note = root

        j = 0
        notes = 0
        for j in range(16):
            if j > 0 and probability(i * 5):
                melody += "r"

            else:
                count = 1 if probability(25) else 2
                for i in range(count):
                    change = choice([-1, 0, 0, 1])
                    if probability(75):
                        change *= 2
                        if probability(75):
                            change *= 1.5
                    if probability(25):
                        note = root
                    note += int(change)
                    notes += 1

                try:
                    melody += scale[note]
                except IndexError:
                    note = root
                    melody += scale[note]



        melodies.append(melody)

    final_melody = ""
    bass = ""
    drums = ""

    print(melodies)

    bars = 256
    while bars > 0:
        reps = choice([4, 2, 1])
        this_mel = choice(melodies)
        if probability(50):
            upbeat = ""
            if probability(75):
                rest = "r"
            if probability(50):
                if probability(50):
                    upbeat = "r"
                rest = "rr"
            else:
                rest = "rrr"
            this_mel = upbeat+"".join([note + rest for note in split_mel(this_mel)][:16])

        cadence = choice([[0, 4] * 4,
                          [0, 3, 4]* 3])
        print(scale)
        print(cadence)
        bass_notes = [scale[i] for i in cadence]
        print(bass_notes)


        bass += choice(riddims)[0].format(*bass_notes)
        bars -= (reps * 8)

        drums += choice(beats)

        if probability(75):
            final_melody += this_mel * reps
        else:
            final_melody += ("r" * 16) * reps

    print(final_melody)

    speed = randint(10, 20)

    # Music
    # List of effects(0:None / 1:Slide / 2:Vibrato / 3:FadeOut)
    pyxel.sound(2).set(
        note=final_melody,
        tone="t",
        volume=("1"),
        effect=(""),
        speed=speed,
    )

    pyxel.sound(1).set(
        note=bass,
        tone="P",
        volume=("3"),
        effect=(""),
        speed=speed,
    )

    pyxel.sound(3).set(
        note=drums,
        tone="N",
        volume=("3"),
        effect=(""),
        speed=speed,
    )

    # pyxel.sound(3).set(
    #     note=harmony1 * 2 + harmony2 * 2, tone="t", volume="5", effect="f", speed=20
    # )
    # pyxel.sound(4).set(
    #     note=("f0 r a4 r  f0 f0 a4 r" "f0 r a4 r   f0 f0 a4 f0"),
    #     tone="n",
    #     volume="6622 6622 6622 6426",
    #     effect="f",
    #     speed=20,
    # )

    pyxel.music(0).set([], [1], [2], [3])
