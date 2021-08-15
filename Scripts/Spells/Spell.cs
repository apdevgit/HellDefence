using UnityEngine;

public abstract class Spell : MonoBehaviour {

    private Transform _caster = null;

    public  Transform caster
    {
        get { return _caster; }
        set { _caster = value; }
    }
}
