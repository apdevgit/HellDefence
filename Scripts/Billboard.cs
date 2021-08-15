using UnityEngine;

public class Billboard : MonoBehaviour {

    void Update()
    {
        Vector3 proj = Vector3.Project(transform.position - Camera.main.transform.position, Camera.main.transform.right);

        int side;
        if (proj.normalized == Camera.main.transform.right)
        {
            side = 1;
        }
        else
        {
            side = -1;
        }

        transform.LookAt(Camera.main.transform.position + Camera.main.transform.right * side * proj.magnitude);
    }

}