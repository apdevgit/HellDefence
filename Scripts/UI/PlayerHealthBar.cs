using UnityEngine;
using UnityEngine.UI;

public class PlayerHealthBar : MonoBehaviour
{
    [SerializeField] private PlayerNumber _playerNumber;
    [SerializeField] private RectTransform currentHealthBar;
    [SerializeField] private Text _healthText;

    private LivingEntity _livingEntity;

    private float healthBarPosX;
    private float healthBarWidth;

    void Start()
    {
        healthBarPosX = currentHealthBar.localPosition.x;
        healthBarWidth = currentHealthBar.rect.width;

        if (_playerNumber == PlayerNumber.P1)
        {
            _livingEntity = GameController.instance.player1Instance.GetComponent<LivingEntity>();
        }
        else if(_playerNumber == PlayerNumber.P2)
        {
            _livingEntity = GameController.instance.player2Instance.GetComponent<LivingEntity>();
        }
    }

    void Update()
    {
        float healthQuota = _livingEntity.GetHealthQuota();
        float newPosX = (healthBarPosX - healthBarWidth * (1 - healthQuota));
        currentHealthBar.localPosition = new Vector3(newPosX, currentHealthBar.localPosition.y, currentHealthBar.localPosition.z);

        _healthText.text = _livingEntity.health + "/" + _livingEntity.maxHealth;

        Color color = currentHealthBar.GetComponent<Image>().color;
        if (healthQuota > .5f)
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
