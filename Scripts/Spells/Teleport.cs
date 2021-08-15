using UnityEngine;

public class Teleport : Spell
{
    private AudioSource _audioSource;
    private AudioClip _audioClip;

    private PlayerSpell _playerSpell;

    void Awake()
    {
        _playerSpell = caster.GetComponent<PlayerSpell>();

        Vector3 pointToCastTo = caster.GetComponent<PlayerSpell>().pointToCastTo;
        pointToCastTo.y = transform.position.y;

        _audioSource = GetComponent<AudioSource>();
        _audioClip = Resources.Load("teleportSound") as AudioClip;

        transform.position = caster.position;
        transform.LookAt(_playerSpell.pointToCastTo);

        float range = Vector3.Distance(transform.position, pointToCastTo);

        Ray newRay = new Ray(transform.position, transform.forward);
        RaycastHit hitInfo;

        float tpDistance;

        if (Physics.Raycast(newRay, out hitInfo, range, 1 << LayerMask.NameToLayer("Wall")))
        {
            tpDistance = Vector3.Distance(transform.position, new Vector3(hitInfo.point.x, transform.position.y, hitInfo.point.z));
        } 
        else
        {
            tpDistance = range;
        }

        caster.transform.Translate(Vector3.forward * tpDistance, Space.Self);

        _audioSource.PlayOneShot(_audioClip);
        Destroy(gameObject, _audioClip.length);
    }
}
