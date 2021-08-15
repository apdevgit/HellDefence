using UnityEngine;
using UnityEngine.UI;

public class HealthBar : MonoBehaviour {

    [SerializeField] private RectTransform currentHealthBar;
    private delegate float getHealthPercentageDel();
    private getHealthPercentageDel getHealthQuota;

    private float healthBarPosX;
    private float healthBarWidth;

	void Awake () {
        // Scale healthbar canvas to .3 based on parent's scale
        float scale = .3f / transform.parent.parent.GetComponent<Transform>().localScale.x;
        transform.parent.localScale = Vector3.one * scale;
        //

        healthBarPosX = currentHealthBar.localPosition.x;
        healthBarWidth = currentHealthBar.rect.width;

        Transform grandParent = transform.parent.parent;

        if (grandParent.GetComponent<LivingEntity>() != null)
        {
            getHealthQuota = grandParent.GetComponent<LivingEntity>().GetHealthQuota;
        }
        else
        {
            getHealthQuota = null;
        }
	}
	
	void Update () {
        if(getHealthQuota == null) { return; }

        float healthQuota = getHealthQuota();
        float newPosX = (healthBarPosX + healthBarWidth * healthQuota);
        currentHealthBar.localPosition = new Vector3(newPosX, currentHealthBar.localPosition.y, currentHealthBar.localPosition.z);
        Color color = currentHealthBar.GetComponent<Image>().color;
        if(healthQuota > .5f)
        {
            color.r = 0;
        }
        else
        {
            color.r = 1 - healthQuota;
        }

        color.g = healthQuota;
        currentHealthBar.GetComponent<Image>().color = color;
    }
}
