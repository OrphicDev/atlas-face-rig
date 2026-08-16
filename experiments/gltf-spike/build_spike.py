"""F0-E.7 — action de preuve bakee sur les os DEF et les morphs."""
import argparse, json, math, os, sys
try: sys.stdout.reconfigure(line_buffering=True)
except Exception: pass
import bpy
from mathutils import Vector
RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRAMES = [(1, "neutral"), (10, "blink_L_100"), (20, "blink_R_100"),
          (30, "mouthClose_100"), (40, "jaw_20"), (50, "jaw_32"),
          (60, "gaze_left"), (70, "gaze_right"), (80, "neutral")]
MORPH = {"blink_L_100": "TMP_blink.L", "blink_R_100": "TMP_blink.R",
         "mouthClose_100": "TMP_mouthClose"}
a = argparse.ArgumentParser()
a.add_argument("--output", required=True); a.add_argument("--reference", required=True)
a.add_argument("--motion", required=True)
o = a.parse_args(sys.argv[sys.argv.index("--") + 1:])
Rp = lambda p: p if os.path.isabs(p) else os.path.join(RACINE, p)
run = bpy.data.objects["GEO_face_runtime"]; rig = bpy.data.objects["TMP_F0_JAW_RIG"]
J = json.load(open(Rp(o.motion), encoding="utf-8"))
sc = bpy.context.scene; sc.frame_start = 1; sc.frame_end = 80
rig.animation_data_create(); rig.animation_data.action = bpy.data.actions.new("TMP_SPIKE")
kb = run.data.shape_keys
kb.animation_data_create(); kb.animation_data.action = bpy.data.actions.new("TMP_SPIKE_MORPH")
pb = rig.pose.bones["TMP_jaw"]; pb.rotation_mode = "XYZ"
REF = {"frames": {}}
for f, pose in FRAMES:
    sc.frame_set(f)
    pb.rotation_euler = (0, 0, 0); pb.location = (0, 0, 0); pb.scale = (1, 1, 1)
    for k in kb.key_blocks:
        if k.name != "Basis": k.value = 0.0
    if pose in MORPH: kb.key_blocks[MORPH[pose]].value = 1.0
    elif pose.startswith("jaw_"):
        pb.rotation_euler.x = math.radians(float(pose.split("_")[1]))
    pb.keyframe_insert("location", frame=f)
    pb.keyframe_insert("rotation_euler", frame=f)
    pb.keyframe_insert("scale", frame=f)
    for k in kb.key_blocks:
        if k.name != "Basis": k.keyframe_insert("value", frame=f)
    bpy.context.view_layer.update()
    REF["frames"][str(f)] = {"pose": pose,
        "jaw_rot_x_deg": round(math.degrees(pb.rotation_euler.x), 6),
        "morphs": {k.name: round(k.value, 6) for k in kb.key_blocks if k.name != "Basis"}}
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(Rp(o.output)))
json.dump(REF, open(Rp(o.reference), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("SPIKE_OK", len(FRAMES), "frames | actions",
      [x.name for x in bpy.data.actions])
