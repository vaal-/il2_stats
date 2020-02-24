
class Coalition:
    neutral = 0
    coal_1 = 1
    coal_2 = 2

    Allies = 1
    Axis = 2
    Entente = 3
    CentralPowers = 4


class Country:
    neutral = 0
    USSR = 101
    GreatBritain = 102
    USA = 103
    Germany = 201
    Italy = 202
    Japan = 203
    France = 301
    GreatBritainWW1 = 302
    UnitedStatesWW1 = 303
    Belgium = 304
    Russia = 305
    GermanyWW1 = 401
    AustriaHungary = 402


COALITION_ALIAS = {
    0: Coalition.neutral,
    1: Coalition.coal_1,
    2: Coalition.coal_2,
    3: Coalition.coal_1,
    4: Coalition.coal_2,
}


GAME_CLASSES = (
    'CAeroplaneFragment',
    'CAerostat',
    'CAerostatAI',
    'CAIPoi',
    'CAirfield',
    'CAnimationOperator',
    'CAttachedVehicle',
    'CBallistics',
    'CBanner',
    'CBatchBallistics',
    'CBatchExplosion',
    'CBatchTrash',
    'CBatchTrashAnimated',
    'CBFManager',
    'CBlocksArray',
    'CBombSiteAim',
    'CBot',
    'CBotAimingHead',
    'CBotCharacter',
    'CBotController',
    'CBotFieldController',
    'CBotHead',
    'CBotInputController',
    'CCameraOperator',
    'CCloudSky',
    'CClusterBallistics',
    'CCommanderInputController',
    'CComplexTrigger',
    'CCumulativeRocket',
    'CDFMission',
    'CDistantLOD',
    'CDummyObject',
    'CEjectionPlace',
    'CEjectorController',
    'CFlag',
    'CFlareGun',
    'CForestBody',
    'CGameChat',
    'CGameMission',
    'CInfluenceArea',
    'CMouseControlCameraOperator',
    'CParachute',
    'CParachutedContainer',
    'CParatroopersCreator',
    'CPhysPlatformRadioTurretAI',
    'CPlane',
    'CPlaneAI',
    'CPlaneInputController',
    'CPlatformTank',
    'CRobotCameraOperator',
    'CRocket',
    'CSharedGroup',
    'CShip',
    'CShipAI',
    'CSolidTrash',
    'CSpotlight',
    'CSpotter',
    'CStaticBlock',
    'CStaticEmitter',
    'CStaticVehicle',
    'CSubmarine',
    'CTank',
    'CTerrainArray',
    'CTorpedo',
    'CTrainAI',
    'CTrainLocomotive',
    'CTrainWagon',
    'CTrash',
    'CTrashAnimated',
    'CTruck',
    'CTurret',
    'CTurretCamera',
    'CTurretRadioAI',
    'CTurretRadioAIInputController',
    'CTurretRiffle',
    'CVehicleAI',
    'CVehicleExplosionTurret',
    'CVehicleInputController',
    'CVehicleRangefinderTurret',
    'CVehicleRangefinderTurretAI',
    'CVehicleRocketTurret',
    'CVehicleRocketTurretAI',
    'CVehicleTorpedoTurret',
    'CVehicleTorpedoTurretAI',
    'CVehicleTurret',
    'CVehicleTurretAI',
    'CVehicleTurretInputController',
    'CWindsock',
)
