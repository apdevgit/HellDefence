using UnityEngine;

public class Cast : MonoBehaviour {

    [SerializeField] private GameObject _spell;

    private Transform _castPoint;

    void Awake()
    {
        InitializeCastPoint(transform);
    }

    public void CastSpell()
    {
        GameObject spell = _spell;
        spell.SetActive(false);
        GameObject castedSpell = Instantiate(spell, _castPoint.position, transform.rotation) as GameObject;
        castedSpell.GetComponent<Spell>().caster = transform;
        castedSpell.SetActive(true);
    }

    private void InitializeCastPoint(Transform transform)
    {
        foreach (Transform tr in transform)
        {
            if (tr.name == "CastPoint")
            {
                _castPoint = tr;
                return;
            }
            else
            {
                InitializeCastPoint(tr);
            }
        }
    }
}
