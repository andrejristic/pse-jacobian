"""Generate a 256x256 app icon: the 3-to-1 fiber (three preimages on the hidden
C*-orbit) — the visual signature of the counterexample."""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

out = sys.argv[1] if len(sys.argv) > 1 else "pse-jacobian.png"

fig = plt.figure(figsize=(2.56, 2.56), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
ax.set_facecolor("#0f2233")
fig.patch.set_facecolor("#0f2233")

# hidden C*-orbit through the base preimage (1, -3/2, 13/2) projected to (x,y)
t = np.concatenate([np.linspace(-2.0, -0.35, 200), np.linspace(0.35, 2.0, 200)])
x = 1.0 / t
y = -1.5 * t
ax.plot(x, y, color="#7fd1e6", lw=2.2, alpha=0.9)

# three colliding preimages (x,y projection)
pts = [(0, 0), (1, -1.5), (-1, 1.5)]
for px, py in pts:
    ax.scatter([px], [py], s=260, color="#d1495b", edgecolors="white",
               linewidths=2, zorder=5)

ax.set_xlim(-3, 3); ax.set_ylim(-3.2, 3.2)
ax.text(0.5, 0.07, "PSE·J", transform=ax.transAxes, ha="center",
        color="white", fontsize=22, fontweight="bold")
fig.savefig(out, dpi=100, facecolor=fig.get_facecolor())
print("wrote", out)
