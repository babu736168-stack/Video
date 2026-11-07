# Rahasya Lab (रहस्य लैब): YouTube channel kit

A ready-to-use brand and setup kit for a Hindi/Hinglish channel of short science and mystery
explainers, the kind of video this repo already makes (Tunguska, Roopkund, deodorant facts).

**Want a different name?** Change the `BRAND` block at the top of `make_branding.py`, run
`python3 make_branding.py`, and find-and-replace "Rahasya Lab" in this file.
Other names that fit the same idea: *Sach Ki Khoj*, *Gyaan Detective*, *Kyun Aur Kaise*, *Fact Lab Hindi*.
Before you commit to one, search YouTube for it and check that the handle is free.

---

## 1. Create the channel (about 10 minutes, on your phone or PC)

1. Sign in to YouTube with the Google account you want to own the channel.
2. **Use a Brand Account** so you can add managers later without sharing your password:
   profile picture → *Settings* → *Add or manage your channel(s)* → **Create a channel** → enter `Rahasya Lab`.
3. Set the **handle**: `@RahasyaLab` (backups: `@RahasyaLabHindi`, `@RahasyaLabIN`).
4. **Verify the channel** with your phone number at youtube.com/verify. This unlocks custom thumbnails and videos longer than 15 minutes.
5. Open **YouTube Studio → Customisation** and upload:

| Field | File | Spec |
|---|---|---|
| Picture | `out/profile_800.png` | 800×800, shown as a circle (`out/profile_preview_circle.png` shows how it looks) |
| Banner | `out/banner_2560x1440.png` | 2560×1440. Text stays inside the 1546×423 safe area (`out/banner_safe_zones_preview.png`) |
| Video watermark | `out/watermark_150.png` | 150×150, display "Entire video" |

## 2. Channel description (paste into Customisation → Basic info)

```
Rahasya Lab mein hum duniya ke sabse ajeeb rahasyon aur roz-marra ki science ko
60 second mein, simple Hindi mein samjhaate hain.

🔍 Unsolved mysteries: Tunguska, Roopkund Skeleton Lake, aur bahut kuch
🧪 Everyday science: aapke ghar ki cheezein kitni safe hain?
✅ Myth-busting: viral claims ka fact-check, sources ke saath

Har video research-based hai. Sources har video ki description mein milenge.

📅 Naye Shorts: har Tuesday, Thursday aur Saturday
🔔 Subscribe karein aur bell dabayein, taaki koi rahasya miss na ho!

Business / collaboration: [your business email]
```

**Links** (Basic info → Add link): Instagram, plus a business email once you have one.
Create a separate address such as rahasyalab.official@gmail.com rather than using your personal email.

**Channel keywords** (Studio → Settings → Channel → Basic info):
```
hindi science, science facts hindi, unsolved mysteries hindi, rahasya, mystery in hindi,
tunguska event, roopkund lake, science shorts, myth busting hindi, health facts hindi,
facts in hindi, gyaan, amazing facts, rahasya lab
```

## 3. Settings checklist (Studio → Settings)

- [ ] **Channel → Basic info**: Country = India (this affects monetisation eligibility).
- [ ] **Channel → Advanced**: Audience = "No, set this channel as not made for kids".
- [ ] **Upload defaults** (saves time on every upload):
  - Title: leave empty. Description: the footer from §5.
  - Tags: `rahasya lab, hindi science, facts in hindi, science shorts`
  - Category: **Education**. Language: **Hindi**. Caption certification: none.
  - Licence: Standard YouTube Licence. Comments: "Hold potentially inappropriate comments for review".
- [ ] **Altered or synthetic content**: in each upload, answer the "Altered content" question honestly.
  Narration from an AI voice that reads your script and animated, clearly illustrated graphics
  are not "realistic" content, so the usual answer is **No**. Answer **Yes** if a video shows
  realistic AI-made footage of real people, places or events.
- [ ] **Community → Automated filters**: add blocked words for spam (`telegram`, `whatsapp me`, `crypto`, `investment`).

## 4. Channel layout

**Playlists** (create these before the first upload):

| Playlist | What goes in it |
|---|---|
| 🔍 Duniya Ke Rahasya (Unsolved Mysteries) | Tunguska, Roopkund, … |
| 🧪 Ghar Ki Science (Everyday Science) | Deodorant, … |
| ✅ Sach Ya Jhooth? (Myth-busting) | Fact-checks of viral claims |
| 🌍 English Versions | The `VIDEO_LANG=en` renders |

**Home tab** (Customisation → Layout): Featured video for returning subscribers = your best Short;
sections = Shorts, then each playlist above.

## 5. Upload templates for the videos already in this repo

Use one footer on every video. Put it in Upload defaults:

```
──────────
📚 Sources: [paste links]
🔔 Subscribe: https://www.youtube.com/@RahasyaLab?sub_confirmation=1
📅 New Shorts every Tue / Thu / Sat

Disclaimer: Ye video sirf jaankari ke liye hai. Health se jude faislon ke liye doctor se salah lein.
#RahasyaLab #HindiFacts #Science
```

### Tunguska (`tunguska_demo/out/tunguska_demo.mp4`)
- **Title:** `1908 mein Siberia mein kya phata tha? 💥 Tunguska ka Rahasya #shorts`
- **Description:** `30 June 1908 ko Siberia ke jungle mein ek dhamaka hua jisne 2,000 sq km ke ~8 crore ped gira diye, lekin wahan koi crater nahi mila. Scientists aaj kya maante hain?`
- **Tags:** `tunguska event, tunguska hindi, siberia explosion, asteroid, 1908, science mystery hindi`
- **Playlist:** Duniya Ke Rahasya
- **Thumbnail / cover:** `out/thumbnail_template_tunguska.png` (for a long video, swap the "?" circle for a frame from the video)

### Roopkund Skeleton Lake (`roopkund_demo/out/roopkund_demo.mp4`)
- **Title:** `Himalaya ki jheel mein 100s kankaal 💀 Roopkund ka sach #shorts`
- **Description:** `Uttarakhand mein ~5,000 m ki oonchai par Roopkund jheel mein 1942 mein sainkadon kankaal mile. 2019 ki DNA study ne bataya ki ye log ~1,000 saal ke antar par mare the!`
- **Tags:** `roopkund, skeleton lake, roopkund lake mystery, uttarakhand, himalaya mystery, hindi facts`
- **Playlist:** Duniya Ke Rahasya
- **Cover:** `out/shorts_cover_roopkund.png`

### Deodorant (`deodorant_v2` Hindi HD render)
- **Title:** `Deodorant spray kitna khatarnak? 😳 Sach jaaniye #shorts`
- **Tags:** `deodorant side effects, deodorant hindi, aerosol spray, benzene, health facts hindi`
- **Playlist:** Ghar Ki Science
- **Thumbnail:** `out/thumbnail_template_deodorant.png`
- Health topic: keep the disclaimer in the footer and put the source links in the description.

**Shorts note:** for Shorts you pick a cover frame in the YouTube app instead of uploading a thumbnail.
Ending each video on a branded frame (like `shorts_cover_*.png`) gives you a good frame to pick.

## 6. Publishing plan, first 30 days

| Week | Goal |
|---|---|
| 1 | Publish the 3 existing videos (Tue / Thu / Sat). Pin a comment asking a question ("Agla rahasya kaunsa?"). |
| 2–4 | 3 new Shorts per week from the same pipeline. Reply to every comment in the first hour. |
| End of month | Studio → Analytics: look at *Shown in feed vs swiped away* and *average % viewed*. Make more of whatever holds viewers past 70 %. |

Topic ideas for the existing engine: Bermuda Triangle (what the data says), Lonar crater lake,
the Wow! signal, Kuldhara ghost village, the Baghdad battery, "Do microwaves cause cancer?",
"Does cracking your knuckles cause arthritis?", "Is RO water bad for you?".

Posting time: India audiences are most active around 6–9 pm IST. Schedule uploads for about 6 pm
and adjust once Analytics → *When your viewers are on YouTube* has data.

## 7. Monetisation milestones (YouTube Partner Programme, India)

| Tier | Requirement |
|---|---|
| Early access (fan funding: memberships, Super Thanks) | 500 subscribers, 3 public uploads in the last 90 days, **and** 3,000 watch hours in 12 months **or** 3 M Shorts views in 90 days |
| Full (ad revenue) | 1,000 subscribers **and** 4,000 watch hours in 12 months **or** 10 M Shorts views in 90 days |

These thresholds change from time to time. Check Studio → **Earn** for the current numbers.

Keep scripts original and fact-checked, list sources, and vary each video's visuals and story.
YouTube's "inauthentic / mass-produced content" policy can block monetisation for channels where
every upload looks like a template.

## Files

```
channel/
├── CHANNEL.md               ← this playbook
├── make_branding.py         ← regenerates everything in out/ (edit BRAND to rename)
└── out/
    ├── profile_800.png                  profile picture
    ├── profile_preview_circle.png       preview of the circular crop
    ├── banner_2560x1440.png             channel banner
    ├── banner_safe_zones_preview.png    banner with phone / tablet / desktop zones marked
    ├── watermark_150.png                video watermark ("subscribe" button)
    ├── thumbnail_template_tunguska.png  1280×720 thumbnail template
    ├── thumbnail_template_deodorant.png
    └── shorts_cover_roopkund.png        1080×1920 Shorts end frame / cover
```
