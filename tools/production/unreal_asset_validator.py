"""Explicitly registered UE editor validator; scoped to opt-in asset contracts.

Call register({asset_object_path: contract}) from a qualification or batch recipe.
No automatic discovery claim: Python validation exists only in that editor session.
"""
import math
import unreal as u

CONTRACTS = {}
OBSERVATIONS = []
INSTANCES = []


def check_asset(asset, contract):
    errors = []
    known = {'class', 'dimensions_cm', 'dimension_tolerance_cm', 'required_bones',
             'required_sockets', 'required_assets', 'required_binding_ids', 'minimum_frames'}
    if not contract or set(contract) - known:
        return ['Empty contract or unsupported requirements: ' + str(sorted(set(contract) - known))]
    if not asset: return ['Missing primary asset']
    expected_class = contract.get('class')
    if expected_class and asset.get_class().get_name() != expected_class:
        errors.append('Unexpected asset class')
    if 'dimensions_cm' in contract:
        dimensions = contract['dimensions_cm']
        if (not isinstance(dimensions, list) or len(dimensions) != 3
                or any(not isinstance(x, (int, float)) or not math.isfinite(x) or x <= 0 for x in dimensions)):
            return ['dimensions_cm must contain three finite positive dimensions']
        if not isinstance(asset,u.StaticMesh): errors.append('Dimension check requires a StaticMesh in this validator version')
        else:
            ext=asset.get_bounds().box_extent
            actual=[2*ext.x,2*ext.y,2*ext.z]
            tolerance=contract.get('dimension_tolerance_cm',0.1)
            if any(abs(a-b)>tolerance for a,b in zip(actual,contract['dimensions_cm'])):
                errors.append('Wrong scale or bounds: '+str(actual))
    if isinstance(asset,u.SkeletalMesh):
        modifier=u.SkeletonModifier()
        if not modifier.set_skeletal_mesh(asset): errors.append('Cannot inspect skeleton')
        else:
            names={str(x) for x in modifier.get_all_bone_names()}
            for bone in contract.get('required_bones',[]):
                if bone not in names: errors.append('Missing bone: '+bone)
        for socket in contract.get('required_sockets',[]):
            if not asset.find_socket(socket): errors.append('Missing socket: '+socket)
    elif contract.get('required_sockets') or contract.get('required_bones'):
        errors.append('Rig requirements supplied for a non-skeletal asset')
    for path in contract.get('required_assets',[]):
        if not u.EditorAssetLibrary.does_asset_exist(path): errors.append('Missing dependency: '+path)
    if isinstance(asset,u.LevelSequence):
        present={str(b.get_id()) for b in asset.get_bindings()}
        for binding in contract.get('required_binding_ids',[]):
            if binding not in present: errors.append('Missing sequence binding: '+binding)
        if contract.get('minimum_frames',0) > asset.get_playback_end()-asset.get_playback_start():
            errors.append('Insufficient sequence duration')
    elif contract.get('required_binding_ids') or contract.get('minimum_frames'):
        errors.append('Sequence requirements supplied for a non-sequence asset')
    return errors


@u.uclass()
class WCCreatureContractValidator(u.EditorValidatorBase):
    @u.ufunction(override=True)
    def k2_can_validate_asset(self,in_asset):
        return in_asset.get_path_name() in CONTRACTS

    @u.ufunction(override=True)
    def k2_validate_loaded_asset(self,in_asset):
        errors=check_asset(in_asset,CONTRACTS[in_asset.get_path_name()])
        OBSERVATIONS.append({'asset':in_asset.get_path_name(),'errors':errors})
        for error in errors: self.asset_fails(in_asset,error)
        if errors: return u.DataValidationResult.INVALID
        self.asset_passes(in_asset)
        return u.DataValidationResult.VALID


def register(contracts):
    CONTRACTS.clear(); CONTRACTS.update(contracts)
    if not INSTANCES:
        validator=WCCreatureContractValidator()
        u.get_editor_subsystem(u.EditorValidatorSubsystem).add_validator(validator)
        INSTANCES.append(validator)
    return INSTANCES[0]


def validate(asset,contract):
    register({asset.get_path_name():contract}); OBSERVATIONS.clear()
    settings=u.ValidateAssetsSettings()
    settings.set_editor_property('collect_per_asset_details',True)
    settings.set_editor_property('skip_excluded_directories',False)
    settings.set_editor_property('show_if_no_failures',False)
    u.get_editor_subsystem(u.EditorValidatorSubsystem).validate_assets_with_settings(
        [u.EditorAssetLibrary.find_asset_data(asset.get_path_name())],settings)
    if not OBSERVATIONS: raise RuntimeError('Python validator was not invoked by the Unreal subsystem')
    return list(OBSERVATIONS)
