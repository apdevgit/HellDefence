using UnityEngine;
using UnityEngine.UI;
using System.Collections;

public class DamageDealtBillboard : MonoBehaviour {

    [SerializeField] private Text _text;

    private float _floatDistance;
    private float _timeBeforeFade;
    private float _fadeTime;

    private bool _isReady;

    void Awake()
    {
        _isReady = false;

        _floatDistance = 1;
        _timeBeforeFade = 2f;
        _fadeTime = 2f;
    }

    void Update()
    {
        if (_isReady)
        {
            Vector3 proj = Vector3.Project(transform.position - Camera.main.transform.position, Camera.main.transform.right);

            int side = -1;
            if (proj.normalized == Camera.main.transform.right)
            {
                side = 1;
            }
            
            transform.LookAt(Camera.main.transform.position + Camera.main.transform.right * side * proj.magnitude);
            transform.Rotate(50, 0, 0, Space.Self);
        }
    }

    public void SetAndReady(int damageDealt, bool isHeal = false)
    {
        if (isHeal)
        {
            _text.text = "+";
        }
        else
        {
            _text.text = "-";
        }
        _text.text += Mathf.Abs(damageDealt).ToString();
        StartCoroutine(FadeManager());
        _isReady = true;
    }

    public void SetAndReady(int damageDealt, Color color, bool isHeal = false)
    {
        _text.color = color;
        SetAndReady(damageDealt, isHeal);
    }

    private IEnumerator FadeManager()
    {
        float timeCount = 0;
        yield return new WaitForSeconds(_timeBeforeFade);

        while(timeCount < _fadeTime)
        {
            _text.color = new Color(_text.color.r, _text.color.g, _text.color.b, 1 - timeCount / _fadeTime);
            timeCount += Time.deltaTime;
            yield return null;
        }

        Destroy(this.gameObject);
    }
}