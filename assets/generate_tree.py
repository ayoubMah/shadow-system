import matplotlib.pyplot as plt
import os

def generate_skill_tree():
    """Generates a visual skill tree."""
    
    skills = {
        'Strength': ['Iron Body', 'Might'],
        'Intelligence': ['Deep Focus', 'Architect'],
        'Agility': ['Shadow Step', 'Ghost'],
        'Vitality': ['Indomitable', 'Rebirth']
    }
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    
    # Draw logic (simplified)
    y_start = 0.8
    y_gap = 0.2
    x_centers = [0.2, 0.4, 0.6, 0.8]
    
    for i, (stat, skill_list) in enumerate(skills.items()):
        x = x_centers[i]
        ax.text(x, y_start, stat.upper(), ha='center', fontsize=12, fontweight='bold', bbox=dict(facecolor='black', alpha=0.1))
        
        for j, skill in enumerate(skill_list):
            y = y_start - ((j + 1) * y_gap)
            ax.text(x, y, skill, ha='center', fontsize=10, bbox=dict(facecolor='#4285F4', alpha=0.3, boxstyle='round,pad=0.5'))
            ax.plot([x, x], [y_start - 0.05, y + 0.05], color='gray', linestyle='--')

    ax.set_title("SHADOW SYSTEM: EVOLUTION TREE", fontsize=16, fontweight='bold', pad=20)
    
    output_path = os.path.join(os.path.dirname(__file__), '../SKILL_TREE.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Map generated at {output_path}")

if __name__ == "__main__":
    generate_skill_tree()
