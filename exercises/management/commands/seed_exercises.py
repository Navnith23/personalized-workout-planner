from django.core.management.base import BaseCommand
from django.db import transaction

from exercises.models import Exercise


# Each tuple:
# name, movement_pattern, muscle_groups, equipment, difficulty, exercise_type,
# instructions, default_sets, default_reps, default_duration_seconds,
# default_rest_seconds, is_low_impact, is_beginner_safe, tags
EXERCISES = [
    # ---------------- WARM-UP ----------------
    ('Arm Circles', 'mobility', ['shoulders'], 'none', 1, 'warmup',
     'Small to large circles forward and backward to loosen the shoulders.',
     1, '', 60, 0, True, True, ['warmup']),
    ('March in Place', 'gait', ['full_body', 'cardio'], 'none', 1, 'warmup',
     'March in place, driving knees up gently, to raise heart rate.',
     1, '', 120, 0, True, True, ['warmup', 'walking']),
    ('Bodyweight Squat to Stand', 'squat', ['quads', 'glutes'], 'none', 1, 'warmup',
     'Slow bodyweight squats focusing on smooth range of motion, not speed or load.',
     1, '', 90, 0, True, True, ['warmup']),
    ('Cat-Cow Stretch', 'mobility', ['core', 'back'], 'none', 1, 'warmup',
     'On hands and knees, alternate arching and rounding the spine slowly.',
     1, '', 90, 0, True, True, ['warmup', 'mobility']),
    ('Leg Swings', 'mobility', ['hamstrings', 'glutes'], 'none', 1, 'warmup',
     'Holding onto support, swing one leg forward/back, then side to side.',
     1, '', 90, 0, True, True, ['warmup']),

    # ---------------- SQUAT PATTERN ----------------
    ('Chair-Assisted Sit-to-Stand', 'squat', ['quads', 'glutes'], 'none', 1, 'main_strength',
     'Sit on a sturdy chair and stand up, using hands on knees for assistance if needed.',
     2, '8-12', None, 60, True, True, ['beginner']),
    ('Bodyweight Squat', 'squat', ['quads', 'glutes'], 'none', 2, 'main_strength',
     'Feet shoulder width, lower hips back and down, keep chest tall, return to standing.',
     3, '10-15', None, 60, True, True, []),
    ('Goblet Squat', 'squat', ['quads', 'glutes'], 'dumbbells', 2, 'main_strength',
     'Hold a dumbbell vertically at chest height, squat down keeping torso upright.',
     3, '8-12', None, 75, True, True, []),
    ('Kettlebell Goblet Squat', 'squat', ['quads', 'glutes'], 'kettlebell', 3, 'main_strength',
     'Hold a kettlebell at chest height by the horns, squat down and drive through the heels.',
     3, '8-12', None, 75, True, True, []),
    ('Barbell Back Squat', 'squat', ['quads', 'glutes'], 'barbell', 4, 'main_strength',
     'Bar racked on upper back, squat to depth keeping the spine neutral, drive up.',
     4, '5-8', None, 120, True, False, []),
    ('Jump Squat', 'squat', ['quads', 'glutes'], 'none', 4, 'main_strength',
     'Perform a bodyweight squat and explode upward into a jump, landing softly.',
     3, '6-10', None, 90, False, False, []),
    ('Wall Sit', 'squat', ['quads'], 'none', 2, 'accessory',
     'Back against a wall, slide down until knees are near 90 degrees, hold.',
     2, '', 30, 45, True, True, []),

    # ---------------- HINGE PATTERN ----------------
    ('Glute Bridge', 'hinge', ['glutes', 'hamstrings'], 'none', 1, 'main_strength',
     'Lie on back, knees bent, lift hips by squeezing glutes, lower with control.',
     3, '10-15', None, 45, True, True, ['beginner']),
    ('Romanian Deadlift (Dumbbell)', 'hinge', ['hamstrings', 'glutes'], 'dumbbells', 3, 'main_strength',
     'Hold dumbbells in front of thighs, hinge at the hips keeping a soft knee bend, lower to mid-shin, return.',
     3, '8-12', None, 75, True, True, []),
    ('Kettlebell Deadlift', 'hinge', ['hamstrings', 'glutes'], 'kettlebell', 3, 'main_strength',
     'Hinge at the hips to grip the kettlebell, drive through heels to stand tall.',
     3, '8-12', None, 75, True, True, []),
    ('Barbell Deadlift', 'hinge', ['hamstrings', 'glutes', 'back'], 'barbell', 5, 'main_strength',
     'Hinge down to grip the bar, brace the core, drive through the floor to stand.',
     4, '4-6', None, 150, True, False, []),
    ('Single-Leg Hip Hinge (Bodyweight)', 'hinge', ['hamstrings', 'glutes'], 'none', 3, 'accessory',
     'Balance on one leg, hinge forward reaching toward the floor, return to standing.',
     2, '6-10', None, 60, True, True, []),

    # ---------------- LUNGE PATTERN ----------------
    ('Assisted Split Stance', 'lunge', ['quads', 'glutes'], 'none', 1, 'main_strength',
     'Using support for balance, step into a shallow split stance and gently shift weight.',
     2, '6-10', None, 60, True, True, ['beginner']),
    ('Bodyweight Reverse Lunge', 'lunge', ['quads', 'glutes'], 'none', 2, 'main_strength',
     'Step one leg back, lower the back knee toward the floor, push back to standing.',
     3, '8-10', None, 60, True, True, []),
    ('Dumbbell Walking Lunge', 'lunge', ['quads', 'glutes'], 'dumbbells', 3, 'main_strength',
     'Holding dumbbells at your sides, step forward into a lunge, alternating legs as you travel.',
     3, '8-10', None, 75, True, True, []),
    ('Bulgarian Split Squat', 'lunge', ['quads', 'glutes'], 'bench', 4, 'main_strength',
     'Rear foot elevated on a bench, lower into a lunge on the front leg, drive back up.',
     3, '8-10', None, 90, True, False, []),

    # ---------------- HORIZONTAL PUSH ----------------
    ('Wall Push-Up', 'push_horizontal', ['chest', 'triceps'], 'none', 1, 'main_strength',
     'Hands on a wall at shoulder height, bend elbows to bring chest toward the wall, push back.',
     2, '8-12', None, 45, True, True, ['beginner']),
    ('Incline Push-Up', 'push_horizontal', ['chest', 'triceps'], 'none', 2, 'main_strength',
     'Hands on a sturdy elevated surface, perform a push-up with a shallower angle than the floor.',
     3, '8-12', None, 60, True, True, []),
    ('Knee Push-Up', 'push_horizontal', ['chest', 'triceps'], 'none', 2, 'main_strength',
     'Knees on the floor, hands under shoulders, lower chest down and push back up.',
     3, '8-12', None, 60, True, True, []),
    ('Push-Up', 'push_horizontal', ['chest', 'triceps'], 'none', 3, 'main_strength',
     'Plank position, lower chest to just above the floor, push back to full arm extension.',
     3, '8-15', None, 60, True, True, []),
    ('Dumbbell Bench Press', 'push_horizontal', ['chest', 'triceps'], 'bench', 3, 'main_strength',
     'Lying on a bench, press dumbbells up from chest level to full extension.',
     3, '8-12', None, 75, True, True, []),
    ('Barbell Bench Press', 'push_horizontal', ['chest', 'triceps'], 'barbell', 4, 'main_strength',
     'Lying on a bench, lower the bar to the chest and press back to full extension.',
     4, '6-10', None, 90, True, False, []),

    # ---------------- VERTICAL PUSH ----------------
    ('Dumbbell Overhead Press (Seated)', 'push_vertical', ['shoulders', 'triceps'], 'dumbbells', 2, 'main_strength',
     'Seated or standing, press dumbbells overhead from shoulder height to full extension.',
     3, '8-12', None, 75, True, True, []),
    ('Pike Push-Up', 'push_vertical', ['shoulders', 'triceps'], 'none', 4, 'main_strength',
     'Hips high in a pike position, lower the head toward the floor and press back up.',
     3, '6-10', None, 75, True, False, []),
    ('Barbell Overhead Press', 'push_vertical', ['shoulders', 'triceps'], 'barbell', 4, 'main_strength',
     'Standing, press the bar from shoulder height to overhead, keeping the core braced.',
     4, '6-8', None, 90, True, False, []),
    ('Resistance Band Overhead Press', 'push_vertical', ['shoulders', 'triceps'], 'resistance_bands', 2, 'main_strength',
     'Stand on the band, press handles from shoulder height overhead.',
     3, '10-15', None, 60, True, True, []),

    # ---------------- HORIZONTAL PULL ----------------
    ('Resistance Band Row', 'pull_horizontal', ['back', 'biceps'], 'resistance_bands', 2, 'main_strength',
     'Anchor the band, pull handles toward the ribs, squeezing shoulder blades together.',
     3, '10-15', None, 60, True, True, ['beginner']),
    ('Dumbbell Bent-Over Row', 'pull_horizontal', ['back', 'biceps'], 'dumbbells', 3, 'main_strength',
     'Hinge forward slightly, row dumbbells toward the hips, squeezing the back.',
     3, '8-12', None, 75, True, True, []),
    ('Barbell Bent-Over Row', 'pull_horizontal', ['back', 'biceps'], 'barbell', 4, 'main_strength',
     'Hinge forward, row the bar to the lower ribs, control the descent.',
     4, '6-10', None, 90, True, False, []),
    ('Inverted Row', 'pull_horizontal', ['back', 'biceps'], 'pullup_bar', 3, 'main_strength',
     'Under a bar set at hip height, pull the chest toward the bar with straight legs.',
     3, '8-12', None, 75, True, False, []),

    # ---------------- VERTICAL PULL ----------------
    ('Resistance Band Pulldown', 'pull_vertical', ['back', 'biceps'], 'resistance_bands', 2, 'main_strength',
     'Anchor the band overhead, pull the handles down toward the chest.',
     3, '10-15', None, 60, True, True, ['beginner']),
    ('Assisted Pull-Up (Band)', 'pull_vertical', ['back', 'biceps'], 'pullup_bar', 4, 'main_strength',
     'Loop a band over the bar and under a knee/foot for assistance, pull chin over the bar.',
     3, '5-8', None, 90, True, False, []),
    ('Pull-Up', 'pull_vertical', ['back', 'biceps'], 'pullup_bar', 5, 'main_strength',
     'Hang from the bar, pull the chin over the bar with control, lower fully.',
     4, '4-8', None, 90, True, False, []),

    # ---------------- CORE ----------------
    ('Dead Bug', 'core', ['core'], 'none', 1, 'core',
     'Lying on back, arms up and knees bent 90 degrees, slowly extend opposite arm and leg.',
     2, '8-10', None, 45, True, True, ['beginner']),
    ('Bird Dog', 'core', ['core', 'back'], 'none', 1, 'core',
     'On hands and knees, extend opposite arm and leg while keeping the spine stable.',
     2, '8-10', None, 45, True, True, ['beginner']),
    ('Modified Plank (Knees)', 'core', ['core'], 'none', 1, 'core',
     'Forearms and knees on the floor, hold a straight line from head to knees.',
     2, '', 20, 30, True, True, []),
    ('Plank', 'core', ['core'], 'none', 2, 'core',
     'Forearms and toes on the floor, hold a straight line from head to heels.',
     2, '', 30, 30, True, True, []),
    ('Side Plank (Knees)', 'core', ['core'], 'none', 2, 'core',
     'On one forearm with knees bent, lift the hips to form a straight line.',
     2, '', 20, 30, True, True, []),
    ('Hanging Knee Raise', 'core', ['core'], 'pullup_bar', 4, 'core',
     'Hang from the bar, raise the knees toward the chest with control.',
     3, '8-12', None, 60, True, False, []),

    # ---------------- CARDIO / GAIT ----------------
    ('Easy Walk', 'gait', ['cardio'], 'none', 1, 'cardio',
     'Walk at a comfortable, conversational pace outdoors or on a treadmill.',
     1, '', 900, 0, True, True, ['walking', 'low_impact']),
    ('Brisk Walk', 'gait', ['cardio'], 'none', 2, 'cardio',
     'Walk at a pace that raises your heart rate while still able to talk in short sentences.',
     1, '', 900, 0, True, True, ['walking']),
    ('Stationary Bike (Easy)', 'gait', ['cardio'], 'cardio_machine', 1, 'cardio',
     'Cycle at a light, steady resistance and comfortable cadence.',
     1, '', 900, 0, True, True, ['cycling', 'low_impact']),
    ('Stationary Bike (Moderate)', 'gait', ['cardio'], 'cardio_machine', 2, 'cardio',
     'Cycle at a moderate resistance, breathing noticeably harder but sustainable.',
     1, '', 900, 0, True, True, ['cycling']),
    ('Jogging', 'gait', ['cardio'], 'none', 3, 'cardio',
     'Jog at a steady, sustainable pace.',
     1, '', 900, 0, False, False, ['running']),
    ('Interval Bike Sprints', 'gait', ['cardio'], 'cardio_machine', 4, 'cardio',
     'Alternate 30 seconds of hard effort with 90 seconds of easy pedaling.',
     1, '', 900, 0, True, False, ['hiit', 'cycling']),

    # ---------------- MOBILITY / COOL-DOWN ----------------
    ("Standing Quad Stretch", 'mobility', ['quads'], 'none', 1, 'mobility',
     'Hold your ankle behind you, gently pulling the heel toward the glutes.',
     1, '', 60, 0, True, True, ['cooldown']),
    ('Seated Hamstring Stretch', 'mobility', ['hamstrings'], 'none', 1, 'mobility',
     'Seated with one leg extended, gently reach toward the toes.',
     1, '', 60, 0, True, True, ['cooldown']),
    ('Chest Doorway Stretch', 'mobility', ['chest'], 'none', 1, 'mobility',
     'Forearm on a doorframe, gently rotate away to feel a stretch across the chest.',
     1, '', 60, 0, True, True, ['cooldown']),
    ("Child's Pose", 'mobility', ['back'], 'none', 1, 'mobility',
     'Kneel and sit back onto the heels, reaching arms forward and relaxing the spine.',
     1, '', 60, 0, True, True, ['cooldown']),
    ('Hip Flexor Stretch', 'mobility', ['glutes', 'quads'], 'none', 1, 'mobility',
     'Kneeling lunge position, gently press the hips forward to stretch the front of the hip.',
     1, '', 60, 0, True, True, ['cooldown']),
]


class Command(BaseCommand):
    help = 'Seed the exercise database with a starter library covering all movement patterns, equipment types, and difficulty levels.'

    @transaction.atomic
    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for row in EXERCISES:
            (name, pattern, muscles, equipment, difficulty, ex_type, instructions,
             sets, reps, duration, rest, low_impact, beginner_safe, tags) = row

            obj, created = Exercise.objects.update_or_create(
                name=name,
                defaults=dict(
                    movement_pattern=pattern,
                    muscle_groups=muscles,
                    equipment=equipment,
                    difficulty=difficulty,
                    exercise_type=ex_type,
                    instructions=instructions,
                    default_sets=sets,
                    default_reps=reps,
                    default_duration_seconds=duration,
                    default_rest_seconds=rest,
                    is_low_impact=low_impact,
                    is_beginner_safe=beginner_safe,
                    tags=tags,
                )
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded exercises: {created_count} created, {updated_count} updated. '
            f'Total in database: {Exercise.objects.count()}.'
        ))
