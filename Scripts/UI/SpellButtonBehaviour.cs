using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(RectTransform))]
public class SpellButtonBehaviour : MonoBehaviour {

    private PlayerNumber _playerNumber;
    private PlayerCooldown _playerCooldown;

    public SpellName representedSpell;

    private Image image;
    private RectTransform rectTransform;
    private Text text;

    private int bWidth;
    private int bHeight;

    public SpellButtonBehaviour(SpellName spellName)
    {
        representedSpell = spellName;
    }

    void Start()
    {
        if(_playerNumber == PlayerNumber.P1)
        {
            _playerCooldown = GameController.instance.player1Instance.GetComponent<PlayerCooldown>();
        }
        else if(_playerNumber == PlayerNumber.P2)
        {
            _playerCooldown = GameController.instance.player2Instance.GetComponent<PlayerCooldown>();
        }

        bWidth = 40;
        bHeight = 40;

        image = GetComponent<Image>();
        rectTransform = GetComponent<RectTransform>();

        image.sprite = GameDictionary.GetSpellIcon(representedSpell);
        rectTransform.sizeDelta = new Vector2(bWidth, bHeight);


        // Initialize font..
        GameObject go = new GameObject();
        go.AddComponent<RectTransform>().sizeDelta = rectTransform.rect.size;
        text = go.AddComponent<Text>();
        text.text = "";
        text.fontSize = 32;
        text.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
        text.alignment = TextAnchor.MiddleCenter;
        text.color = new Color(1, .6f, 0);
        go.transform.SetParent(this.transform, true);
        go.transform.localPosition = new Vector3(0, 0, 0);

    }

    public void SetTheNumberOfThePlayer(PlayerNumber playerNumber)
    {
        _playerNumber = playerNumber;
    }

    void Update()
    {
        int cd = (int)_playerCooldown.GetSpellCooldownPercentage(representedSpell);
        if( cd != 0)
        {
            text.text = (100 - cd).ToString();
        }
        else
        {
            text.text = "";
        }
    }

}
