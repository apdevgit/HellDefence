using UnityEngine;

public class Throw : MonoBehaviour {

    [SerializeField] private GameObject _throwingObject;

    private Transform _throwPoint;

    void Awake()
    {
        InitializeThrowPoint(transform);
    }

    public void ThrowObject( int damage, float hitForce, float speed, float rotationSpeed, Vector3 targetPos, float lifetime)
    {
        GameObject go = _throwingObject;
        go.SetActive(false);
        go = Instantiate(go);
        go.AddComponent<ThrowingObject>().SetVariables(gameObject, damage, hitForce, speed, rotationSpeed, targetPos, lifetime);
        go.transform.position = _throwPoint.position;
        go.transform.LookAt(new Vector3(targetPos.x, go.transform.position.y, targetPos.z), Vector3.up);
        go.SetActive(true);
    }

    private void InitializeThrowPoint(Transform transform)
    {
        foreach (Transform tr in transform)
        {
            if (tr.name == "ThrowPoint")
            {
                _throwPoint = tr;
                return;
            }
            else
            {
                InitializeThrowPoint(tr);
            }
        }
    }
}
