|     | MITSUBISHI |     | ELECTRIC | RESEARCH |     | LABORATORIES |     |
| --- | ---------- | --- | -------- | -------- | --- | ------------ | --- |
https://www.merl.com
| Perception-Aware |            | Model  | Predictive |          |              | Control     | for Constrained |
| ---------------- | ---------- | ------ | ---------- | -------- | ------------ | ----------- | --------------- |
|                  | Control    |        | in Unknown |          | Environments |             |                 |
|                  | Bonzanini, | Angelo | Domenico;  | Mesbah,  | Ali;         | Di Cairano, | Stefano         |
|                  |            |        | TR2023-147 | December |              | 16, 2023    |                 |
Abstract
The operation of autonomous systems is inherently constrained by their surrounding envi-
ronment, which is often time-varying and unknown a priori, necessitating perception using
sensors. Hence, control strategies for autonomous systems must take into account the un-
certainty of the perceived environment in making decisions, while information acquired by
sensors often depends on how the system is operated, e.g., where the sensors are pointed at,
or what and how much sensor information is processed. We introduce a perception-aware
chance-constrained model predictive control (PAC-MPC) strategy that accounts for the un-
certainty of the perceived environment, as well as the dependence of the perception quality
on the control actions. The system and the environment are coupled by chance constraints
due to the uncertainty in the environment estimate, which depends on control actions. We
establish the constraint satisfaction and stability properties of PAC-MPC through appropri-
atedesignofthecostfunctionandterminalset, andproposeaconstructivedesignprocedure
| for the case | of linear dynamics. |     |     |     |     |     |     |
| ------------ | ------------------- | --- | --- | --- | --- | --- | --- |
| Automatica   | 2023                |     |     |     |     |     |     |
2023L˙icensed
(cid:13)c under the Creative Commons BY-NC-ND 4.0 license http://creativecommons.org/licenses/by-nc-
nd/4.0/.
MitsubishiElectricResearchLaboratories,Inc.
201Broadway,Cambridge,Massachusetts02139

Perception-AwareModelPredictiveControl
forConstrainedControlinUnknownEnvironments
AngeloD.Bonzaninia,AliMesbaha,StefanoDiCairanob
aUniversityofCalifornia,Berkeley,CA94720
bCorrespondingAuthor.MitsubishiElectricResearchLaboratories,Cambridge,MA02139.
Abstract
Theoperationofautonomoussystemsisinherentlyconstrainedbytheirsurroundingenvironment,whichisoftentime-varying
and unknown a priori, necessitating perception using sensors. Hence, control strategies for autonomous systems must take
into account the uncertainty of the perceived environment in making decisions, while information acquired by sensors often
depends on how the system is operated, e.g., where the sensors are pointed at, or what and how much sensor information is
processed.Weintroduceaperception-awarechance-constrainedmodelpredictivecontrol(PAC-MPC)strategythataccounts
for the uncertainty of the perceived environment, as well as the dependence of the perception quality on the control actions.
Thesystemandtheenvironmentarecoupledbychanceconstraintsduetotheuncertaintyintheenvironmentestimate,which
dependsoncontrolactions.WeestablishtheconstraintsatisfactionandstabilitypropertiesofPAC-MPCthroughappropriate
designofthecostfunctionandterminalset,andproposeaconstructivedesignprocedureforthecaseoflineardynamics.
Keywords: Controlofconstrainedsystemsunderuncertainty,Nonlinearpredictivecontrol,Perceptionandsensing,
Integrationofcontrolandperception
1 Introduction While perception is often assumed to be independent
fromcontrolactions,thatmayoverlooktheactualcapa-
Autonomoussystems,suchasmobilerobots,automated bilities of advanced sensors. For instance, cameras and
vehiclesanddrones,admitmotionmodelsthataregen- lidars have a limited field-of-view and range, and are
erally accurate, especially when regulated by low-level subject to occlusions, so that the acquired information
controllers. However, the environment where such sys- dependsonsystempositionandattitude.Advancedsen-
temsoperateisoftennotknownapriori andmaychange sorsareoftenequippedwithmechanismsthatallowdif-
dynamically,e.g.,duetothelocationofothervehicleson ferentregionsandamountsoffocus,suchasradarbeam-
theroad,ofworkersonafactoryfloor,ofobstructionsto forming, and hence allow to directly or indirectly ad-
flightpath,orofmarkingsdelimitingtheworkspace.The justthespreadandqualityoftheacquiredinformation.
elements of the environment may not affect the system Basedonthis,thesystemoperationmayimproveifthe
motion dynamics, but rather impose constraints on the controllercanpredicttheimpactofcontroldecisionson
permissible motions and actions, such as containment the uncertainty of the perceived environment informa-
on the workspace, collision avoidance with vehicles or tion and, accordingly, account for such varying uncer-
workers, and safe flyby around obstructions. The envi- tainty in decision-making. For instance, in automated
ronment information is obtained from perception using driving, the control stack may determine an initial tra-
data provided by sensors, e.g., lidar, radar and cam- jectorythatprovidesabetterfieldofvieworavoidsoc-
eras [6]. Since the perception from sensors is imperfect, clusions,whilealsodeterminingthefocusareasforradar
theconstraintsrelatingsystemandenvironmentareun- beamforming. This may reduce the uncertainty in crit-
certainandhencetheperceptionperformanceinreduc- ical road areas, so that more effective trajectories be-
ing the environment uncertainty affects the control de- comesubsequentlyfeasible.Asacomplicatingfactor,ad-
cisions[1,11,17,18]. vancedsensorsinactualapplicationsareequippedwith
on-boardperceptionalgorithmsthatthecontrollermay
leveragebutnotre-design,andhencethedegreesoffree-
Emailaddresses: adbonzanini@berkeley.edu(AngeloD.
Bonzanini),mesbah@berkeley.edu(AliMesbah), domoverperceptionaremorelimited.
dicairano@ieee.org(StefanoDiCairano).
PreprintsubmittedtoAutomatica 22November2023

The interplay between control and perception has re- andstabilityofthesystemstatetoitstargetandofthe
cently received increasing attention. In [8], distance- environment estimate to its steady-state distribution.
dependent measurement models are leveraged to solve Although our method shares similarities with output-
a combined estimation and control problem subject to feedback MPC, see, e.g., [10], we consider a nonlinear
probabilistic collision avoidance. In [5], the control ac- system where, for the practical reasons discussed be-
tions are designed to explore an unknown environment fore,thecontrolalgorithmcannotmodifytheestimator,
while maximizing localization accuracy, but without but only leverage its system actions-dependent perfor-
accounting for the uncertainty evolution. Perception- mance.Furthermore,weleveragetheproblemstructure,
awarecontrolbasedonmodelpredictivecontrol(MPC) specifically the environment being dynamically decou-
ispresentedin[9]totrackareferencewhilemaximizing pled from the system, to obtain stability results for
the visibility of a point of interest. Similar concepts for system state and environment uncertainty, as opposed
planning the motion of an autonomous system, while toconvergence[10].
| concurrently |     | maximizing | the | retention | of  | obstacles | or  |     |     |     |     |     |     |     |     |
| ------------ | --- | ---------- | --- | --------- | --- | --------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
landmarksinthesensorrange(e.g.,thecamera’sfieldof Inwhatfollows,Section2introducesthemodelsforthe
| view) have | also | been | proposed | [7,14,19–21,24–26,28]. |     |     |     |         |                  |     |     |               |     |     |         |
| ---------- | ---- | ---- | -------- | ---------------------- | --- | --- | --- | ------- | ---------------- | --- | --- | ------------- | --- | --- | ------- |
|            |      |      |          |                        |     |     |     | system, | the environment, |     | its | measurements, |     | and | its es- |
Some approaches improve the estimation of the ob- timator. In Section 3, we describe the general design of
stacles/targets by keeping them in the sensor field of PAC-MPC, and Section 4 provides general conditions
view, including by optimizing the observability Grami- for the closed-loop recursive feasibility and stability. In
ans [21,24]. In [15], a learning-based controller that Section 5, we propose a constructive design for PAC-
| combines | perception |     | and control | has | been | presented |     |         |     |                |     |                |     |            |     |
| -------- | ---------- | --- | ----------- | --- | ---- | --------- | --- | ------- | --- | -------------- | --- | -------------- | --- | ---------- | --- |
|          |            |     |             |     |      |           |     | MPC for | the | linear setting |     | that satisfies | the | conditions |     |
that includes estimation of the uncertainty to assess of Section 4. Section 6 presents the simulation results,
unsafe conditions. Nonetheless, the majority of these followedbytheconclusionsinSection7.
| works do | not | consider | the | impact of | the varying |     | envi- |     |     |     |     |     |     |     |     |
| -------- | --- | -------- | --- | --------- | ----------- | --- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
ronment uncertainty on the constraints, and hence on Notation:R,R ,R ,arethesetsofreal,nonnegative
|                 |     |        |             |     |           |          |     |     |     | 0+  | +   |     |     |     |     |
| --------------- | --- | ------ | ----------- | --- | --------- | -------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| the controller, |     | as the | environment | is  | explored. | Further- |     |     |     |     |     |     |     |     |     |
real,positiverealnumbers,respectively,andsimilarfor
integernumbersZ.Wedenoteintervalofnumberswith
| more, ensuring |     | closed-loop |     | stability | in the | presence | of  |     |     |     |     |     |     |     |     |
| -------------- | --- | ----------- | --- | --------- | ------ | -------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
the internal feedback, where perception affects control notations such as Z = {z ∈ Z : a ≤ z < b}. Given
[a,b)
andvice-versa,remainsanon-trivialopenproblem. vectors x y, the i-th component is [x] , the stacking is
i
|     |     |     |     |     |     |     |     |         | [x(cid:48) y(cid:48)](cid:48), |                     |        |        | (cid:107)x(cid:107)2 |     | x(cid:48)Qx. |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | ------------------------------ | ------------------- | ------ | ------ | -------------------- | --- | ------------ |
|     |     |     |     |     |     |     |     | (x,y) = |                                | (cid:107)x(cid:107) | is the | 2-norm | and                  | =   |              |
Q
In this paper, we consider a known nonlinear dynam- For a matrix X, (cid:107)X(cid:107) is the Frobenious norm, where
F
ical system that operates in an environment that is subscriptmaybedroppedifclearfromthecontext,and
| not known | a   | priori. A | given | fixed estimator |     | provides | a   |           |           | P[A] |     |                 |     |       |       |
| --------- | --- | --------- | ----- | --------------- | --- | -------- | --- | --------- | --------- | ---- | --- | --------------- | --- | ----- | ----- |
|           |     |           |       |                 |     |          |     | the trace | is tr(X). |      | is  | the probability |     | of A. | For a |
stochastic estimate of the environment state based on E[x] µx Σx
|             |          |     |      |          |       |        |     | random         | vector | x,      | =          | is the | expectation | and    |     |
| ----------- | -------- | --- | ---- | -------- | ----- | ------ | --- | -------------- | ------ | ------- | ---------- | ------ | ----------- | ------ | --- |
| information | acquired |     | from | sensing, | which | depend | on  |                |        |         |            |        |             |        |     |
|             |          |     |      |          |       |        |     | the covariance |        | matrix. | A normally |        | distributed | random |     |
the system state and input. The system operation is vectorisdenotedbyx∼N (µx,Σx).Themomentsmay
not directly affected by process uncertainty, but rather begroupedasMx =(µx,Σx).Foradiscrete-timesignal
by the uncertainty in the knowledge of environment, x ∈ Rn, x is the value at sampling instant k, x is
|               |            |            |           |     |             |             |        |               | k     |          |        |         |         |          | j|k  |
| ------------- | ---------- | ---------- | --------- | --- | ----------- | ----------- | ------ | ------------- | ----- | -------- | ------ | ------- | ------- | -------- | ---- |
| which affects |            | the system | operation |     | through     | constraints |        |               |       |          |        |         |         |          |      |
|               |            |            |           |     |             |             |        | the predicted |       | value    | at k + | j based | on data | at k,    | and  |
| relating      | the system |            | state and | the | environment |             | state. |               |       |          |        | R       | R       |          |      |
|               |            |            |           |     |             |             |        | x =           | x . A | function | α :    | →       | is      | of class | K if |
|               |            |            |           |     |             |             |        | 0|k           | k     |          |        | 0+      | 0+      |          |      |
Wedesignaperception-awarechance-constrainedMPC it is continuous, strictly increasing, and α(0) = 0. In
(PAC-MPC)1
that uses the environment estimation addition,iflim α(c)=∞,α isofclassK .
|     |     |     |     |     |     |     |     |     |     | c→∞ |     |     |     | ∞   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
modeltopredicttheevolutionoftheenvironmentstate
| and uncertainty, |     | which | is then | used | to enforce | chance |     |     |     |     |     |     |     |     |     |
| ---------------- | --- | ----- | ------- | ---- | ---------- | ------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
constraints [1,11,16,18] between the system and envi- 2 ModelingandProblemDefinition
| ronment. | Thus, | PAC-MPC |     | accounts | for the | effects | of  |     |     |     |     |     |     |     |     |
| -------- | ----- | ------- | --- | -------- | ------- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
the system operation on the perception quality, which Weconsideradiscrete-timesystemdescribedby
| may lead | to a | better | closed-loop | performance. |     | For | ex- |     |     |     |     |     |     |     |     |
| -------- | ---- | ------ | ----------- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ample,PAC-MPCmayyieldatrajectorythatimproves xs =fs(xs,us), (1a)
|                 |        |     |              |         |                 |     |        |     |     | k+1 |                | k k |     |     |      |
| --------------- | ------ | --- | ------------ | ------- | --------------- | --- | ------ | --- | --- | --- | -------------- | --- | --- | --- | ---- |
| the sensing,    | which, | in  | turn,        | reduces | the uncertainty |     | in     |     |     |     |                |     |     |     |      |
|                 |        |     |              |         |                 |     |        |     |     |     | ys =qs(xs,us), |     |     |     | (1b) |
| the environment |        | and | thus reduces | the     | tightening      |     | in the |     |     |     | k              | k k |     |     |      |
chance constraints, possibly resulting in less conserva- Rnx Rnu
|     |     |     |     |     |     |     |     | where xs | ∈   | is the | system | state | vector, | us ∈ |     |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | --- | ------ | ------ | ----- | ------- | ---- | --- |
tivefuturetrajectories.Weproposesuitabledesignsfor
|          |            |     |               |              |           |             |     | is the system                  |        | input vector, |        | ys ∈ Rny   | is the   | system | per-   |
| -------- | ---------- | --- | ------------- | ------------ | --------- | ----------- | --- | ------------------------------ | ------ | ------------- | ------ | ---------- | -------- | ------ | ------ |
| the cost | function   | and | terminal      | constraints, |           | so that     | the |                                |        |               |        |            |          |        |        |
|          |            |     |               |              |           |             |     | formance                       | output | vector,       | fs     | : Rnx ×Rnu | →        | Rnx    | is the |
| PAC-MPC  | guarantees |     | probabilistic |              | recursive | feasibility |     |                                |        |               |        |            |          |        |        |
|          |            |     |               |              |           |             |     | systemstateupdatefunctionandqs |        |               |        |            | :Rnx×Rnu | →Rny   |        |
|          |            |     |               |              |           |             |     | is the system                  |        | performance   | output | function.  |          | System | (1)    |
1 Thispaperextendsourworks[2–4]byprovidingdetailed
|     |     |     |     |     |     |     |     | andxs | areknownatanytimestep,andaresubjectto |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | ------------------------------------- | --- | --- | --- | --- | --- | --- |
proofs,anewmethodforcontrollerdesigninthelinearcase
| that avoids | previous | restrictive |     | assumptions, |     | additional | de- |     |     |     |     |        |     |     |     |
| ----------- | -------- | ----------- | --- | ------------ | --- | ---------- | --- | --- | --- | --- | --- | ------ | --- | --- | --- |
|             |          |             |     |              |     |            |     |     |     | xs  | ∈X, | us ∈U, |     |     | (2) |
tailsonthealgorithms,andextendedsimulationstudies.
2

where X and U are the state and input admissible sets, update. Although the environment evolution (4a) does
respectively.Weassumethefollowing. not depend on (1), the estimate mean and covariance
updates in (5) depend on xs, us due to (4b). This en-
Assumption1 System (1)iscontrollableinX within- ablescapturingthedependencyoftheperceptionperfor-
putinU,andobservablewithrespecttoys. mance on the control decision, e.g., due to field of view
andocclusions,sensorfocusareasandlevels,orifasen-
Remark1 Throughout this paper, system (1) is as- sor adjusts its gain based on focus or range. Often, the
sumed to be known, i.e., deterministic. System uncer- effects of such decisions are appreciable only in the un-
tainty may be accounted for by combining the proposed certainty evolution, i.e., on the covariance update (5b),
method with standard results on MPC for uncertain but(5a)allowsforcapturingalsotheeffectsinthemean.
systems see [22, Ch.3] and references therein, e.g., by Since the environment exogenous input ψ in (4a) is not
first tightening the constraints according to a tube MPC known,in(5)itismodeledasprocessnoise,resultingin
design,andthenapplyingthemethodsdescribedhere. ψ, ζ being distributions described by the first two mo-
ments,µψ,Σψ,andµζ,Σζ,respectively.Suchmoments
are not shown explicitly in (5) since here they are as-
Inadditionto(2),theenvironmentinwhichthesystem sumedtobeconstantforsimplicity,thoughitispossible
operatesimposesadditionalconstraints to extend to the time-varying case. In the remainder of
thepaperwewillusetheshorthandg(Me,ye,xs,us)for
hsxs+hexe ≤hb, l∈Z , (3) thelefthandsideof (5).
l l l [1,nc,]
where hs ∈ Rnx, he ∈ Rmx are known vectors, and Remark2 Estimator (5) is assumed fixed because in
xe ∈ Rm l x is the en l vironment state vector describing practicalapplicationsitisusuallyintegratedinthesens-
ing system and hence not a design choice for the con-
variables imposing constraints on the system, such as
troller. Here, we design a controller that leverages the
positionsofobstacles,velocitiesofotheragentsandan-
dependency of (5) on xs, us, to influence the estimate
gles of boundary markings. The environment evolution
performance and achieve the control objective, and we
modelis
provide suitable conditions on the estimator for this to
succeed.
xe =fe(xe,ψ ), (4a)
k+1 k k
where ψ ∈ Rmψ describes the exogenous inputs to (4a)
While xe is not directly known, (5) may include infor-
and fe : Rmx ×Rmψ → Rmx is the environment state
mationonfe,ifavailable.Theonlyrequirementfor(5)
update function. Model (4) allows for representing sta-
istoproducethefirsttwomomentsµe,Σe ofavaliddis-
tionary,e.g.,boundarymarkingsandfixedobstacles[3],
tribution for xe. Using only the first two moments al-
and moving, e.g., cars and workers [4], elements of the
lows for increased computational tractability, while ad-
environment by formulating constant dynamics or mo-
ditionalmomentscanbeincludedinasimilarway.
tion models, respectively. Thus, the environment state
xecontainsalltheinformationformodelingtheposition
Remark3 In the estimator (5), the covariance up-
and/or motion of the environment elements as needed
date (5b) does not depend on the measurement ye, e.g.,
for prediction of the constraints. However, xe is not di-
as in Kalman filters. Instead, (5a), (5b) depend on the
rectly known, hence its probability distribution is esti-
systemstatesandinputs,whichdescribethedependence
matedbasedonperceivedinformation,
oftheperceptionqualityonthecontrolactions.
ye =qe(xe,ζ ,xs,us), (4b)
k k k k k
Now,wepresenttheproblemaddressedinthispaper.
where ye ∈ Rmy is the environment measurement vec-
tor, ζ ∈Rmζ is the measurement noise, and qe :Rmx × Problem1 Consider system (1) subject to con-
Rmζ ×Rnx ×Rnu → Rmy is the environment measure- straints (2), environment (4), environment estima-
mentfunction.Weconsiderestimatorsthatusethemea- tor (5)andconstraints (3)betweensystemandenviron-
surementsfrom(4b)toprovidethefirsttwomomentsof ment. We want to design a control law that stabilizes
adistributionofxe,namelymeanµe ∈Rmx andcovari- xs in an equilibrium where ys = r for a given output
anceΣe ∈Rmx×mx, setpointr ∈Rny,whilesatisfying (2)and (3),thelatter
inaprobabilisticsenseduetotheuncertaintyin (5). (cid:50)
µe =g (µe,ye,xs,us), (5a)
k+1 µ k k k k
Σe =g (Σe,xs,us), (5b)
k+1 Σ k k k
3 Perception-awareChanceConstrainedMPC
whereg
µ
:Rmx×Rmy×Rnx×Rny →Rmxistheenviron-
ment estimate mean update and g
Σ
:Rmx×mx ×Rnx × We propose a perception-aware chance constrained
Rny →Rmx×mx istheenvironmentestimatecovariance MPC (PAC-MPC) for solving Problem 1. Since the en-
3

vironmentstateisnotdirectlyknown,theenvironment
prediction model is based on the estimator (5). How-
ever,(5)cannotbeusedforpredictionbecauseye isnot
known in advance. Thus, we predict mean and covari-
anceoftheestimateofxe bytheenvironmentpredictor
µˆe =gˆ (µˆe,µy,xs,us), (6a)
k+1 µ k k k k
(cid:16) (cid:17)
Σˆe =gˆ Σˆe,Σy,xs,us , (6b)
k+1 Σ k k k k
whereµˆe ∈Rmx,Σˆe ∈Rmx×mx arethepredictedmean Fig. 1. Schematic of the relation between system, environ-
andcovarianceoftheestimateofxe,gˆ
µ
:Rmx ×Rmy × ment,estimator,andthecontrollawofPAC-MPC.
Rnx×Rny →Rmx andgˆ
Σ
:Rmx×mx×Rmy×my×Rnx×
Rny → Rmx×mx are the environment estimate predic-
tion mean and covariance update, respectively. In (6),
µy isthepredictedmeasurementmeanaccordingtothe
measurement prediction function qy : Rmx × Rnx ×
Rnu →Rmy performance output ys, PAC-MPC aims at stabilizing
µy k =qy(µe k ,xs k ,us k ), (7) xsinanequilibriumsuchthaty k s =r k .Theoverallstate
andΣy isthecovarianceofthemeasurementprediction consistsofxs,µe,Σe,wherethemeanoftheenvironment
error, (cid:15) = ye − µy. In what follows we will use the estimateisguaranteedtoconvergeindependentofxs,us
y
shorthandgˆ(M(e,y),xs,us)torefertothelefthandside by Assumption 2. Hence, PAC-MPC must stabilize the
of (6). The following assumption is related to a “well- augmented state ξ = (xs,Σe). Accordingly, we define a
designed”estimator. cost function that includes a terminal cost F : Rnx ×
Rmx×mx ×Rny → R
0+
and stage cost (cid:96) : Rnx ×Rnu ×
Assumption2 The mean estimator (5a) and mean Rmx×mx ×Rny →R 0+ suchthat
predictor (6a) are asymptotically convergent, i.e.,
µe → µ¯e , and unbiased, i.e., µe = E[xe], for every
k ∞ ∞
realizationofthesequence{(xs,us)}.
k k
V (xs,U ,Σe,r )= (10)
N k k k k
N−1
Assumption 2 can be satisfied by proper estimator and (cid:88)
F(xs ,Σe ,r )+ (cid:96)(xs ,us ,Σe ,r )=
predictor designs. In fact, since the system operation N|k N|k k j|k j|k j|k k
may affect the quality of the measurement (i.e., the co- j=0
F (xs ,r )+F (xs ,Σe ,r )+
variance), but has minimal effects on the measurement c N|k k p N|k N|k k
itself(i.e.,themean),themeanestimatewillusuallynot N−1
(cid:88)
begreatlyaffectedbythesystemstateandinput. (cid:96) (xs ,us ,r )+(cid:96) (xs ,us ,Σe ,r ).
c j|k j|k k p j|k j|k j|k k
j=0
While constraints (2) involve only the state and input
of (1), which are known, constraints (3) involve the en-
vironment state, for which a stochastic distribution is
known from (5) and (6). Thus, (3) are enforced as indi-
vidualchanceconstraints(ICCs)
In (10), N ∈ Z
+
is the prediction horizon; (cid:96)
c
: Rnx ×
Rnu ×Rny → R
0+
and F
c
: Rnx ×Rny → R
0+
are the
P(cid:2) hs l xs+he l xe ≤hb l (cid:3) ≥1−ε l , l∈Z [1,nc,] , (8) c R o m n x tr × o m l x st × ag R e n a y nd → te R rm 0+ in a a n l d co F s p ts : , R re m sp x e × c m ti x v × ely R ,(cid:96) n p y : → Rn R u 0 × +
aretheperception stageandterminalcost,respectively,
whereε istheallowedprobabilityofviolationforthelth (cid:16) (cid:17)
l andU = us ,...,us .
constraint.TheICCs(8)canbeformulatedastightened k 0|k N|k
deterministicconstraints[11,18]
hsxs+[γ(Mˆe)] =hsxs+heµˆe+[γ¯(Σˆe)] ≤hb, (9)
l l l l l l
Stabilizing the environment state estimate covariance,
where γ is the impact of the environment on the con- also prevents an uncontrolled increase of Σe, which
straints,andγ¯ istheconstrainttightening(backoff)pa- would lead to large future tightening values in (9) and
rameterduetotheenvironmentestimateuncertainty. henceapossiblereducedperformanceorevenlossoffea-
sibility.Bycombiningthepredictionmodels(1),(6),(7)
ThecostfunctionofPAC-MPCencodestheobjectiveof and the constraints (2), (9), at each sampling time
Problem1.Foragivenreferencer
k
∈Rny forthesystem k, PAC-MPC solves the finite-horizon optimal control
4

problem Assumption4 Given any two Me = (µe,Σe), Me =
1 1 1 2
(µe,Σe)suchthatγ(Me)≥γ(Me),γ(gˆ(M(e,y),xs,us))≥
2 2 1 2 1
V
N
∗(xs
k
,µe
k
,Σe
k
,r
k
)= γ(gˆ(M(e,y),xs,us))forallxs,us.
2
min V (xs,U ,Σe,r ) (11a)
N k k k k
Uk
s.t. xs =fs(xs ,us ) (11b)
j+1|k j|k j|k Assumption3ensuresthatthepredictordoesnotunder-
Mˆe =gˆ(Mˆ(e,y),xs ,us ) (11c) estimate the constraint tightening with respect to the
j+1|k j|k j|k j|k
environmentmeanandcovarianceestimate,andthein-
Σe =g (Σe ,xs ,us ) (11d)
j+1|k Σ j|k j|k j|k equality can be satisfied by the choice of Σy in accor-
µy =qy(µe,xs ,us ) (11e) dancetothemeasurementgainintheestimator(5).As-
j|k k j|k j|k
(xs ,us )∈X ×U (11f) sumption 4 requires that for any two sets of moments,
j|k j|k the one requiring a larger constraint tightening will re-
hsxs +[γ(Mˆe )] ≤hb(cid:96)∈Z (11g) sultinapredictionthatalsoimposesalargerconstraint
(cid:96) j|k j|k (cid:96) i [1,nc,]
(cid:16) (cid:17) tighteningthanthepredictionoftheotherone.Thus,if
xs ,r ∈Z (Mˆe ) (11h)
N|k k f N|k theuncertainty“mass”accountedforinthechancecon-
xs =xs, µe =µe, Σe =Σˆe =Σe, (11i) straint is larger in one case when compared to another
0|k k 0|k k 0|k 0|k k case,itwillremainlargerafterpredictionisoperatedon
both.Thisamountsto(6)applyingnon-abruptupdates
where Z f ⊆ Rns × Rny is the terminal set that de- totheestimatemoments,andissatisfiedwhentheesti-
pends on the first two moments of the environment es- matorgainisnotexcessivelylarge.
timate,andisusedtoensurerecursivefeasibility,asde-
scribed later. Denoting the solution of (11) by U k ∗ = Remark5 While ideally Σy is chosen equal to the co-
(us,∗,...,us,∗ ), the PAC-MPC law with block dia-
0|k N−1|k varianceofthemeasurementpredictionerror,forthere-
gramshowninFig.1is sults developed in the remainder of this paper it suffices
to choose Σy such that Assumption 3 holds. A method
us
k
=κmpc(xs
k
,Me
k
,r)=us
0
,
|
∗
k
. (12) t
t
h
io
a
n
t
w
le
i
v
th
er
P
a
A
ge
C
s
-
s
M
ce
P
n
C
ar
t
i
o
o-
r
b
e
a
d
s
u
e
c
d
et
o
h
p
e
ti
c
m
on
iz
s
a
e
t
r
i
v
o
a
n
tiv
in
en
c
e
o
s
m
so
bi
f
n
Σ
a
y
-
at the price of an increased computational burden in the
Remark4 In (11), there are two predictors for the
optimalcontrolproblemwaspresentedin[4].
environment estimate covariance: (11d) yields Σe for
cost (11a), while (11c) yields Σˆe for constraints (11g). Theorem1 Let Assumptions 3, 4 hold. Let there exist
Sincethefuturemeasurementsy
k
e areunknown,thepre- a control law κ
f
: Rnx ×Rmx ×Rmx×mx ×Rny → Rnu
dictor (6)includesadditionaluncertaintybyΣy tosafely andasetZ (Me)suchthatif(xs,r)∈Z (Me),
f f
tighten the constraints (11g) Instead, (5b) does not re-
quire y k e, and hence Σe for cost (11a) can be predicted (i) xs ∈X, κ f (xs,Me,r)∈U,
irrespective of the actual measurements. Both Σe and
0|k P(cid:2) hsxs+hexe ≤hb(cid:3) ≥1−ε , i∈Z ,
Σˆe areinitializedtoΣe,in (11i). i i i i [1,nc,]
0|k k (ii) (fs(xs,κ (xs,Me,r)), r)
f
∈Z (gˆ(M(e,y),xs,κ (xs,Me,r))).
f f
4 RecursiveFeasibilityandStabilityConditions
Then, if (11) is feasible at time k for (1), (5) in closed-
We now provide conditions for the design of the termi- loop with (12) and r k+1 = r k , (11) is feasible at time
nal set Z f in (11h) and the terminal cost F in (11a) to k+1withprobabilityatleast
(cid:81)n
i= c 1 ε i .
achieverecursivefeasibilityandstabilityinprobability.
Proof1 By (i), if (xs,r) ∈ Z (Me), it also sat-
f
isfies (2) and (8). Let the solution at time k be
4.1 RecursiveFeasibilityConditions U∗ = (us,∗...us,∗ ), yielding the state trajectory
k 0|k N−1|k
X∗ = (xs,∗...xs,∗ ) and Γ∗ = (γ∗ ...γ∗ ). By the
k 0|k N|k k 0|k N|k
ForastabilizingMPC[23],theterminalsetmustbepos- ICCs (11g), the probability that the initial state at step
itivelyinvariantfor(1),(5)inclosed-loopwithatermi- k+1 satisfies the constraints is (cid:81)nc ε . Using the so-
nalcontroller.Wemakethefollowingassumptions. lution at time k and the terminal i c = o 1 nt i roller κ (·), we
f
construct a candidate solution at k + 1, i.e., U˜ =
k+1
Assumption3 Given any ye from (4b) where Me = (us,∗...us,∗ κ (xs ,Mˆe ,r)), which yields
(µe,Σe) are the moments of the estimate of xe, 1|k N−1|k f N|k N|k
X˜ = (xs,∗...xs,∗ fs(xs,∗ ,κ (xs,∗ ,Mˆe ,r))).
γ(gˆ(M(e,y),xs,us))≥γ(g(Me,ye,xs,us))forallxs,us. k+1 1|k N|k N|k f N|k N|k
For Γ˜ , using X˜ , U˜ , from (6) we obtain
k+1 k+1 k+1
5

γ˜ = γ(gˆ(Mˆ(e,y) ,x˜s ,u˜s )). By Assump- for (11) as long as xs satisfies the constraints in the
ti
j
o
+
n
1|k
3
+
,
1
γ(Me ) ≤
j|k
γ
+
(
1
Mˆe
j|k+
),
1
an
j
d
|k+
b
1
y combining As- initialstep,whichhas
k+
p
1
robabilityatleast
(cid:81)n
i= c 1 ε i .
k+1 1|k
sumptions 3, 4, γ(Mˆe ) ≤ γ(Mˆe ) for all
j|k+1 j+1|k
j ∈ Z . Thus, the constraint tightening does
[1,...N−1] In Corollary 1, the terminal control law κ does not
not increase, and hence all the constraints at steps f
directly depend on the environment information Me.
j ∈ Z are satisfied. Since by (ii) κ makes the
[0,...N−1] f The terminal set Z depends on Me only through the
terminal set invariant for (1), (6), the terminal con- f
constraint tightening γ, and Z does not shrink as γ
straint (11h) is also satisfied. Thus, if x satisfies the f
k+1 decreases.
constraints, which has a probability at least
(cid:81)nc
ε , a
i=1 i
feasiblesolutionof (11)exists.
Remark6 IntheproofsofTheorem1andCorollary1,
Assumptions 3, 4 ensure that the previously predicted
PAC-MPCtrajectoryremainsfeasiblewhentheone-step
InTheorem1,(i)requiresZ f tobecontainedintheset aheadenvironmentpredictionissubstitutedwiththeup-
whereκ f satisfies(2),(8)and(ii)requiresitbeinvariant dated environment estimate, i.e., the tightening of (3)
for (1) in closed-loop with κ f and (6), where Assump- due to ICC (8) does not expand. If Assumptions 3, 4
tions3,4ensureinvariancewiththeconstrainttighten- donothold,besidesastandardconstraintsoftening,one
ingduetoenvironmentprediction.AlthoughTheorem1 maymodifythetighteningγ(Mˆe )tobetheslacksof (3)
isgeneral,adesignoftheterminalcontrollerandtermi- j|k
for the previously predicted PAC-MPC trajectory, when
nal set to satisfy such assumptions may be challenging,
the environment prediction is initialized by the updated
especially since the conditions concurrently involve the
estimate from (5). This ensures that the previous PAC-
designofthepredictorandtheterminalcontroller.If(6)
MPCsolutionisstillfeasiblefor (11),althoughtheprob-
satisfiesadditionalproperties,adecoupleddesignofthe
abilityofsatisfying (3)maybelowerthantheonein (8).
terminalcontrollerκ andthepredictorgˆachievessim-
f As in [10], this may be done if the solution to (11) with
ilarproperties.
tighteningfrom (8)resultsininfeasibility.
Corollary1 Consider κ (xs,Me,r) = κ (xs,r),
f f
Z (Me) = Z¯ (γ(Me)) such that if γ(Me) ≤ γ(Me),
f f 1 2 4.2 StabilityConditions
then Z¯ (γ(Me)) ⊇ Z¯ (γ(Me)). Let Assumptions 3, 4
f 1 f 2
hold,andlet(6)besuchthat γ(gˆ(M(e,y),xs,κ (xs,r)))≤
γ(Me)forall(x ,r)∈Z (Me).Letκ (xs,r f ),Z (Me) Next,weinvestigateconditionsunderwhichthecontrol
besuchthat,if(x s s,r)∈Z f (Me), f f law (12) stabilizes (1) with the environment state esti-
f mateprovidedby(5).Intherestofthissection,forsim-
plicity of notation, r = 0 for all k ∈ Z , and hence
(i) xs ∈X, κ (xs,r)∈U, k 0+
f omitted. The full state of (1), (5) is ϕ = (xs,µe,Σe),
P(cid:2) hsxs+hexe ≤hb(cid:3) ≥1−ε , i∈Z , where µe, Σe affect only the ICCs (9). Due to Assump-
(ii) (fs(
i
xs,κ (x
i
s,r)), r
i
)∈Z (M
i
e).
[1,nc,]
tion2,µeasymptoticallyconvergestoE[xe],andweonly
f f needconditionsthatstabilizeξ =(xs,Σe)toanequilib-
rium ξr = (xr,Σr), being the equilibrium state for (1)
Then,if (11)isfeasibleattimekandr =r for (1),
k+1 k andtheequilibriumcovariance(i.e.,uncertainty)for(5).
(5)inclosed-loopwith (12),(11)isfeasibleattimek+1
withprobabilitygreaterorequalto
(cid:81)nc
ε .
i=1 i Proposition1 Thefunction
Proof2 AsforTheorem1,westartbyusing(i)tonote
that,if(xs,r)∈Z (Me),itsatisfiesconstraints(2),(8). (cid:107)ξ(cid:107)=(cid:107)xs(cid:107)+(cid:107)Σe(cid:107) F (13)
f
FollowingthereasoningofTheorem (1),sincenowκ (·)
f
does not depend on Me, the candidate solution at k+1 isanormforξ =(xs,Σe).
is U˜ = (us,∗...us,∗ κ (xs ,r)), which yields
k+1 1|k N−1|k f N|k
X˜ = (xs,∗...xs,∗ fs(xs,∗ ,κ (xs ,r))). Again, Proof3 The function is nonnegative, since it sums the
k+1 1|k N|k N|k f N|k norms of xs and (cid:107)Σe(cid:107) , and it is 0 only if both are 0,
F
we obtain Γ˜ k+1 from X˜ k+1 , U˜ k+1 , (6) as γ˜ j+1|k+1 = i.e., if ξ = (0,0). Given ξ 1 = (xs 1 ,Σe 1 ), ξ 2 = (xs 2 ,Σe 2 ),
γ(gˆ(Mˆ(e,y) ,x˜s ,u˜s )),andγ(Mˆe )≤γ(Mˆe ) (cid:107)ξ 1 +ξ 2 (cid:107) = (cid:107)x 1 +x 2 (cid:107)+(cid:107)Σe 1 +Σe 2 (cid:107) ≤ (cid:107)x 1 (cid:107)+(cid:107)Σe 1 (cid:107)+
for all j j|k ∈ +1 Z j|k+1 j b |k y + c 1 ombining As j s | u k+ m 1 ptions 3 a j n + d 1|k (cid:107)x 2 (cid:107)+(cid:107)Σe 2 (cid:107)=(cid:107)ξ 1 (cid:107)+(cid:107)ξ 2 (cid:107).
[1,...N−1]
4.Hence,alltheconstraintsaresatisfieduptothetermi-
nal constraint. For the latter, if (xs,∗ ,r) ∈ Z (Mˆe ),
N|k f N|k
We denote the dynamics of (1), (5) by ϕ =
then (fs(xs,∗ ,κ (xs,∗ ,r)), r) ∈ Z (Mˆe ) ⊆ k+1
N|k f N|k f N|k Φ(ϕ k ,us k ,y k e), by ς the function that selects ξ from ϕ,
Z f (Mˆe N|k+1 ). Thus there exists a feasible solution i.e., ς(ϕ) = ς((xs,µe,Σe)) = (xs,Σe) = ξ, Φξ = ς ◦Φ,
6

andwewrite(10)as By[23],ifF(ξ)≥(cid:96)(ξ,κ (ϕ))+F(Φξ(ϕ,κ (ϕ),ye)),then
f f
V (ξ,U)=F(ξ )+
N
(cid:88)
−1
(cid:96)(ξ ,us ), (14)
V
N
∗(Φ(ϕ,κmpc(ϕ),ye))−V
N
∗(ϕ)≤−(cid:96)(ξ,κmpc(ϕ))
N N|k j|k j|k ≤−(cid:96)(ξ,0)≤−α l ((cid:107)ξ(cid:107))=−α ∆ ((cid:107)ξ(cid:107)).
j=0
where F(ξ) = F (xs) + F (Σe) and (cid:96)(ξ,us) =
c p
(cid:96) (xs,us) + (cid:96) (Σe). The value function of (11) is
c p
V∗(ϕ)=V∗(xs,µe,Σe). Theorem2 Let Assumption 5 and the conditions of
N N Theorem1orCorollary1hold.Ifforallx ∈Z (Me)
s f
Assumption5 The control stage cost is such that
(cid:96) c (xs,0) ≤ (cid:96) c (xs,us) for all us ∈ U and there exist F c (fs(xs,κ f (ϕ))−F c (xs)+(cid:96) c (xs,κ f (ϕ))≤−M(xs)
functions αc,αp,αc,αp ∈ K such that (cid:96) (xs,0) ≥ (16a)
l l u u ∞ c
αc((cid:107)xs(cid:107)), F (xs) ≤ αc((cid:107)xs(cid:107)) and (cid:96) (Σe) ≥ αp((cid:107)Σe(cid:107)), F (g (Σe,xs,κ (ϕ)))−F (Σe)
l c u p l p Σ f p
F p (Σe)≤α u p((cid:107)Σe(cid:107)). +(cid:96) p (ξ,κ f (ϕ))≤M(xs) (16b)
Assumption6 The control law u = κ (ϕ) is such
f are satisfied, where M is a nonnegative function, at ev-
that for all xs ∈ Z (Me), F(ξ) ≥ (cid:96)(ξ,κ (ϕ)) +
f f ery step the closed-loop (1), (5), (12) has probability at
F(Φξ(ϕ,κ
f
(ϕ),ye))and
least
(cid:81)n
i= c 1 ε i to evolve according to the Lyapunov func-
tion (15).
fs(xs,κ (ϕ))∈Z (gˆ(Me,My,xs,κ (ϕ))). (cid:4)
f f f
Proof5 Theorem 1 and Corollary 1 ensure that (11)
is recursively feasible with probability
(cid:81)nc
ε at every
Assumption5isstandardforMPCcostfunctions(11a), i=1 i
step and that κ makes the terminal set invariant, i.e.,
f
see[22],andAssumption6isrelatedtotheexistenceof
fs(xs,κ (ϕ))∈Z (gˆ(M(e,y),xs,κ (ϕ))).If (16)holds,
localcontrolLyapunovfunction,andwillbesatisfiedby f f f
F(ξ)≥(cid:96)(ξ,κ (ϕ))+F(Φξ(ϕ,κ (ϕ),ye)).Thus,theas-
thedesignsproposedlater. f f
sumptionsofLemma1areallsatisfied.Hence,withprob-
ability equal to that of satisfying the chance constraints,
We first prove that under Assumptions 5, 6 V N ∗(ϕ), is a (cid:81)nc ε ,theclosed-loopdynamicsevolveaccordingtothe
Lyapunovfunctionofξ for(1)inclosed-loopwith(12). i=1 i
Lyapunovfunction (15)forξ =ς(ϕ).
Lemma1 Let Assumptions 5, 6 hold, then there exist
Remark7 Theorem 2 proves the stability of ξ =
functionsα ,α ,α ∈K suchthat
l u ∆ ∞ (xs,Σe) = ς(ϕ), since we consider that the system
α ((cid:107)ξ(cid:107))≤V∗(ϕ)≤α ((cid:107)ξ(cid:107)), (15a) operation affects the measurement quality, i.e., the co-
l N u variance, and not its value, i.e., the mean. Proving the
V
N
∗(Φ(ϕ,κmpc(ϕ),ye))−V
N
∗(ϕ)≤−α
∆
((cid:107)ξ(cid:107)), (15b)
stability of ϕ also requires guaranteeing the stability of
themeanestimateµe,bymodifyingAssumption2.
whenever (11) is feasible for (xs,µe,Σe) = ϕ and for
k k k
Φ(ϕ,κmpc(ϕ),ye).
Proof4 By construction V∗(ϕ) ≥ (cid:96)(ξ,0). Under the 5 ConstructiveDesignforLinearDynamics
N
assumptions,wecanchoose
The conditions in Section 4 for recursively feasibility
α ((cid:107)ξ(cid:107))=min{(αc(1/2(cid:107)ξ(cid:107)),αp(1/2(cid:107)ξ(cid:107)))} and closed-loop stability are established for a general
l l l
nonlinearsystemand,hence,itishardtoderiveageneral
since by (13) (cid:107)Σe(cid:107) ≥ 1/2 (cid:107)ξ(cid:107) for (cid:107)Σe(cid:107) ≥ (cid:107)xs(cid:107), and the constructiveproceduretosatisfythem.Next,wederivea
oppositeholdswhen(cid:107)xs(cid:107)≥(cid:107)Σe(cid:107).Thus, constructivedesignprocedureforachievingtherecursive
feasibility and stability properties of Section 4 for the
α ((cid:107)ξ(cid:107))≤αc(1/2(cid:107)ξ(cid:107))≤αp((cid:107)Σe(cid:107))≤(cid:96) (Σe) caseinwhich(1),(2),(4),(5),(6)arelinear.Let(1)be
l l l p
≤(cid:96)(ξ,0)≤V∗(ϕ). thelinearsystem
N
xs =Asxs +Bsus, (17a)
k+1 k k
For the upper bound, [23] guarantees that there exists ys =Esxs, (17b)
k k
c>0suchthatcF(ξ)≥V∗(ϕ).Then,
N
andtheconstraintsin(2)bepolyhedral
V∗(ϕ)≤cF (xs)+cF (Σe)≤cαc((cid:107)xs(cid:107))+cαp((cid:107)Σe(cid:107))
N c p u u
≤cα u c((cid:107)ξ(cid:107))+cα u p((cid:107)ξ(cid:107))=α u ((cid:107)ξ(cid:107)). Hxxs ≤Kx, Huus ≤Ku. (18)
7

For(5),weconsideralinearestimatorbasedontheopen- withtheadditionaldynamicsr =r =randη =
k+1 k k+1
loopenvironmentmodel η . Set (23) is the MCAS of a lifted system, where η
k
describes the tightening margin on the ICCs. We de-
xe k+1 =Aexe k +Beψ k , (19a) fineO ∞ (η)={(xs,r):(xs,r,η)∈O ∞ }.
ye =Ce(xs,us)xe +De(xs,us)ζ , (19b)
k k k k k k k Corollary2 Let (1),(2)be (17),(18),respectively.Let
Z (Me)=O (γ(Me)),(6)besuchthatforall(x ,r)∈
f ∞ s
where ψ ∼ N(µψ,Σψ) and ζ ∼ N(µζ,Σζ). The envi-
k k Z (Me), γ(gˆ(M(e,y),xs,κ (xs,r))) ≤ γ(Me). If As-
ronmentestimatemeanandcovarianceevolveas f f
sumptions 3, 4 hold and (11) is feasible at time k and
r = r , (11) is feasible at time k+1 for (17), (20),
µe k+1 =Λ k µe k +Beµψ−L k y k e, (20a) (1 k 2 + ) 1 with k probabilitygreaterorequalto (cid:81)n i= c 1 ε i .
Σe =Λ ΣeΛ(cid:48) +Q+R , (20b)
k+1 k k k k
Proof6 Weprovetheresultbyshowingthat,underthe
where C = Ce(xs,us), De = De(xs,us), L = statedassumptions,theassumptionsofCorollary1hold,
L(xs,us) k ,Λ =Λ(xs k ,us k )=A k e+L C ,Q k = k BeΣψ k Be(cid:48), which then provide the result. The choice of Z f (Me)
k k k k k k k satisfies:(i)inCorollary1bythedefinitionof (23)when
and R(xs,us) = L DeΣζ(L De)(cid:48). As in (4), the mea-
k k k k k k η = γ(Me); and (ii) in Corollary 1 since the MCAS is
surement (19b) depends on the system states and in-
positivelyinvariant[13]for (17)inclosed-loopwith(22).
puts to describe the variable perception quality. Based
Inaddition,O (η )⊇O (η )whenη ≥η duetothe
on(20),thepredictor(6)takestheform ∞ 1 ∞ 2 2 1
monotonicityofO withrespecttotheadmissibleregion.
∞
Due to the remaining assumptions, all the assumptions
µˆe k+1 =Λ k µˆe k +Beµψ−L k µy k , (21a) ofCorollary1aresatisfied,henceprovingthestatement.
Σˆe =Λ ΣˆeΛ(cid:48) +Q+Rˆ , (21b)
k+1 k k k k
where Rˆ = Rˆ(xs,us) = L (DeΣζDe(cid:48) +Σy)L(cid:48) to ac-
k k k k k k k k 5.2 StabilizingTerminalCostDesign
countforthemeasurementpredictionerror.
Toprovideconstructivestabilityconditions,weconsider
We consider a constant reference r for ys. Under As-
the case where Λ(xs,us) = Λ = Ae + LCe, i.e., the
sumption 1, given r, by setting [ru] to nominal values
i estimation error update matrix does not depend on the
fortheinputs[u] thatonlyaffect(19b),i.e.,perception,
i system state and input. The dependency on state and
we obtain unique constant setpoints rx and ru for xs
inputcanstillbepresentinR(xs,us),aswellasinLand
and us, respectively. Next, we design the terminal con-
Ce, if it cancels out in the product. For the linear case,
straint (11h) and cost (11a) such that (17), (18), (19),
in(10)weconsiderthecontrolstageandterminalcosts
(8) in closed-loop with (12), (20) satisfy the properties
ofSection4.
(cid:96) (xs,us,r)=||xs−rx||2 +||us−ru||2 , (24a)
c Qc Rc
F (xs,r)=||xs−rx||2 , (24b)
5.1 TerminalSetDesign c Pc
where Q ,R ,P > 0 are weight matrices. For the per-
c c c
Duetolinearityof (17),(18),weconsiderterminalcon-
ceptioncost,weconstructthesteady-stateenvironment
trollersoftheform
covarianceby
u=κ
f
(xs,r)=K
f
xs+G
f
r, (22) Σr =ΛΣrΛ(cid:48)+Q+R(rx,ru).
where K is a stabilizing gain for (17) and G provides ForΣ¯e =Σe−Σr,R¯(xs,us)=R(xs,us)−R(rx,ru),we
f f
unitary dc-gain from r to y when (17) is in closed-loop obtain the error of the covariance matrix with respect
with(22).Thechallengeinconstructingtheterminalset to the steady-state as Σ¯e = ΛΣ¯eΛ(cid:48)+R¯(xs,us). The
k+1 k k k
using [13] is that (9) depends nonlinearly on Σe, which perceptionstageandterminalcostsin(10)arechosenas
isnotconstantandcannotbepredictedopen-loopsince
it is affected by the control actions. Let the admissible (cid:96) (Σe)=S (cid:107)Σ¯e(cid:107)2, (25a)
references be constrained by Hrr ≤ Kr, we construct p k c k F
the maximum constrained admissible set (MCAS) [13] F (Σe)=W
N
(cid:88)
p−1
ρh(cid:107)ΛhΣ¯eΛh(cid:48) (cid:107)2, (25b)
for(17)inclosed-loopwith(22), p k c k F
h=0
O ∞ ={(xs 0 ,r 0 ,η): Hxxs k ≤Kx, Huκ f (xs,r)≤Ku, where N ∈Z , ρ∈R are design parameters. The
p + [1,∞)
Hrr k ≤Kr,hs i xs k +[η] i ≤hb i ,i∈Z [1,nc,] , ∀k ∈Z 0+ }, terminal perception cost (25a) is the sum of the envi-
(23) ronmentcovariancematrixerrors,overhorizonN ,from
p
8

the terminal state at the end of the prediction horizon that holds for every (cid:37) ∈ R+, and (26d) (second upper
for the closed-loop (17), (22). Thus, (25a) is the finite- bounding).Thus,
horizonapproximationoftheperceptioncost-to-go.We
allow N p ≥ 1 because if N p = 1 as in [2], the cost de- F (Σe)+(cid:96) (Σe)−F (Σe)−M(xs)
crease condition requires the Frobenius norm of the co- p + p p
varianceerrortocontractinasinglestep,whichinturn ≤S c (cid:107)Σ¯e(cid:107)2 F −W c (cid:107)Σ¯e(cid:107)2 F +ρNpW c (cid:107)ΛNpΣ¯eΛNp (cid:48) (cid:107)2 F
requires(cid:107)Λ(cid:107) F <1thatisnotalwayspossibletoachieve. ≤W (cid:107)Σ¯e(cid:107)2(ρNp(cid:107)ΛNp(cid:107)2 +S /W −1).
c F F c c
Instead, with a convergent estimator (Assumption 2),
therealwaysexistsN
p
∈Z
+
suchthat(cid:107)ΛNp(cid:107)
F
<1.
Since ρNp(cid:107)ΛNp(cid:107)2
F
≤ 1−S
c
/W
c
by (26b), (16b) holds
In the general case, N may need to be computed by andalltheconditionsofTheorem2hold.
p
simulations.However,whenΛ(xs,us)=As+LCs,itis
straightforward to find a value for N that satisfies the
p
condition.
Conditions (26) of Corollary 3 require choosing N
p
Corollary3 Consider (17),(18),and (22)andtheen-
such that (cid:107)ΛNp(cid:107)2
F
< c/ρN
p
, c < 1. By Assumption 2,
vironment (19). Let the environment estimator be (20) lim h→∞ (cid:107)Λh(cid:107)2 F = 0, and hence it is always possible to
where Λ(xs,us) = Λ, Z (Me) = O (γ(Me)) and the satisfy it. The coefficient ρ is related to (cid:37) in Young’s
f ∞
assumptions of Corollary 2 hold. If there exist W ,S ∈ inequality from (26a). We could set ρ = 1 if the (non-
c c
R , (cid:37) ∈ R , M ≥ 0, N ∈ Z , such that for all squared) Frobenius norm is used in (25), which would
+ + c p +
(x ,r)∈Z (Me), result in a more challenging optimization problem.
s f
Condition (26c) bounds the increase in the perception
ρ≥(1+(cid:37)), (26a) cost due to the difference between R(xs,κ f (xs,r)) and
thesteady-stateR(rx,ru).Suchboundisaccountedfor
ρNp(cid:107)ΛNp(cid:107)2 ≤1−S /W , (26b)
F c c in (26d) to ensure that any increase in perception cost
xs(cid:48)M c xs ≥ N (cid:88) p−1 ρh(cid:107)ΛhR¯(xs,κ (xs,r))Λh(cid:48) (cid:107)2, (26c) i M s co a m n p d e K nsat c e a d n b b y e a d l e a t r e g r e m r i d n e e c d re i a t s e e ra o t f iv t e h l e y, c p on o t s r s o ib l l c y os b t y .
(1+(cid:37)−1)W f F c f
c i=0 simulationandlinearregression,sincetheyonlydepend
P c −(As+BsK f )(cid:48)P c (As+BsK f )≥ onaninitialstatexs,where(xs,r)∈Z f (Me).
K(cid:48)R K +Q +M , (26d)
f c f c c
Remark8 Extending the design to a general Λ(xs,us)
thenwith(12),theevolutionofξ =(xs,Σe)satisfies(15) requiresconsideringtheh-stepsstatetransitionmatrices
ateachstepwithprobabilityatleast (cid:81)nc ε . (cid:81)h Λ(xs ,κ (xs ,r)), where xs is the (cid:96)-steps ahead
i=1 i (cid:96)=0 ((cid:96)) f ((cid:96)) ((cid:96))
predictionofxs basedon (17),(22)forthetime-varying
Proof7 We prove that the conditions of Theorem 2 system, as opposed to Λh, and defining a reference tra-
hold.Duetoκ f satisfyingCorollary2,theterminalcon- jectory for the covariance matrix that converges to the
troller has the properties in Corollary 1. Next, we show setpoint, so that one can express the error of the covari-
t r h k a + t 1 ( = 16 0 ) f h o o r l s d i s m . p A li s ci i t n y a T n h d eo o r m em it i 2 t. , C w h e oo c s o i n n s g id M er (x r s k ) = = a R¯ n ( c x e s m ,u a s t ) r . ixasΣ¯e k+1 =Λ(xs,κ f (xs))Σ¯e k Λ(xs,κ f (xs))(cid:48)+
xs(cid:48)M xs, (16a) amounts to (26d). For (16b), let R¯ = k k
c f
R¯(xs,κ(xs))andΣe =ΛΣeΛ(cid:48)+Q+R (xs),then
+ f Remark9 Forperceptioncost(cid:96) (ξ,u)=S (tr(Σe)−tr(Σr))2,
p c
Np−1 F p (ξ)=W c (tr(Σe)−tr(Σr))2 asin[3],stabilitycannot
F (Σe)=W (cid:88) ρh(cid:107)Λh(R¯ (xs)+ΛΣ¯eΛ(cid:48))Λh(cid:48) (cid:107)2 be proved directly since the trace is a semi-norm with
p + c f F
non-unique zero. Thus, we can only prove asymptotic
h=0
stabilitytoasetofequilibria.Byimposingtheconstraints
=W (cid:88)
Np
ρh−1(cid:107)ΛhΣ¯eΛh(cid:48) +Λh−1R¯ (xs)Λh−1(cid:48) (cid:107)2 Σ¯e 0 > 0, R¯ k > 0 for all k ∈ Z 0+ , where Σ¯e, R¯ are dif-
c f F ferences from setpoints, Σ¯e > 0 for every k ∈ Z and
h=1 k 0+
stability can be proved using arguments from LaSalle’s
≤W (cid:88)
Np
ρh−1((1+(cid:37))(cid:107)ΛhΣ¯eΛh(cid:48) (cid:107)2 invarianceprinciple.
c F
h=1
+(1+(cid:37)−1)(cid:107)Λh−1R¯ (xs)Λh−1(cid:48) (cid:107)2)
f F
6 CaseStudy
Np
≤W (cid:88) ρh(cid:107)ΛhΣ¯eΛh(cid:48) (cid:107)2 +M(xs),
c F
Fortheeaseofillustration,weshowthebehaviorofPAC-
h=1
MPC on a double integrator case study. A more realis-
where we used Young’s inequality (first upper bounding) tic automated driving case study is described in details
9

in[4].Weconsiderxs ∈R2,us ∈R2 and
(cid:34) (cid:35) (cid:34) (cid:35)
1 0.5 0.5 0 (cid:104) (cid:105)
A= , B = , E = 1 0
0 1 1 0
in (17) with sampling period T = 1. Input [u] ∈ [0,1]
s 2
onlyimpactstheenvironmentmeasurementquality.The
constraintsetsin(2)areX ={x∈R2 : |[x] |≤10, i=
i
1,2}, U = {u ∈ R2 : ,[u] ∈ [−5,5], [u] ∈ [0,1]}, and
1 2
(17)isalsosubjecttotheICCs
(cid:104) (cid:105)
P [xs] −[xe] ≤0 ≥1−0.05, i=1,2, (27)
i i
where xe ∈ R2 is the environment state. We consider
an environment with two elements, both of which are
unknownbutconstantandmeasuredsubjecttonoise,so
that the model is (19), with Ae = I, Be = 0, Ce = Ae,
ζ ∼N(0,I),and
De =(1−β[u ] )D¯, (28)
k k 2
Fig. 2. PAC-MPC for double integrator with input-depen-
where β ∈ (0,1), D¯ ∈ R2×2, showing measurement dent measurements. Closed-loop state, input, and environ-
dependency on [u] . The control objective is to regu- mentcovariancetrajectoriesfordifferentinitialsystemstates
2
late the system state to rx = 2, with ru = 0, and andfixedinitialenvironmentuncertainty(gray),constraints
(dash black), true environment constraints (dash red), per-
theenvironmentestimatecovariancetoitssteady-state
ception input (dash gray), deterministic constraints (dash,
for xs = rx, us = ru. For weights in (24) assigned as
black) . One simulation shown in blue, with corresponding
Q = diag(0.1,0.01), R = diag(0.1,1), the controller
c c ICCs based on environment estimate mean and covariance
is designed as described in Section 5, where the envi- (solid,darkred)(solid,black).
ronment estimator and predictor are (20), (21), respec-
tively, L = −0.45 · I for all k ∈ Z in (20), (21),
k 0+
N =3,ρ=3,S =1,W =2.5in(25).In(26),(cid:37)=2,
p c c
M = 20 · I , Pc, K are obtained by solving (26d)
s 2 f where (cid:96) is a length-scale constant. Fig. 4 shows the
as an LMI, and Z (Me) is the O set (23). Assump- i
f ∞ closed-looptrajectoriesfordifferentsysteminitialstates
tions 1, 5, 6 are known to hold for the chosen system,
and the same initial environment estimate covariance.
cost and terminal set, Assumption 2 holds by the esti-
Also in this case, all the trajectories stabilize to the de-
matordesign,Assumption3holdsbychoosingΣy based
sired steady-state while satisfying the constraints most
on the prediction error, and Assumption 4 holds due to
ofthetimeaccordingto(27),butwithhighersensitivity
the environment model where the disturbances and es-
totheinitialenvironmentestimatecovariance.
timatorerrorarezero-mean,see,e.g.,[10].
Fig.2showstheclosed-looptrajectoriesfordifferentsys-
Toverifythatthechanceconstraintsprovidethedesired
tem initial states and the same initial environment es-
probability of satisfaction of constraints (27), we simu-
timatecovariance.Allthetrajectoriesreachthedesired
lated100MonteCarloruns,eachof200timesteps,when
steady-state while satisfying the constraints according
r = 5.5, i.e., slightly infeasible, to activate the con-
to (27). Fig. 2 also shows that the closed-loop trajecto- x
straints often and to get a tighter approximation of the
riesoftheenvironmentcovariancehaslowsensitivityto
empiricalprobabilityofconstraintsatisfaction.Thisre-
thesysteminitialstate.Fig.3showstheclosed-looptra-
sultedina98%constraintsatisfaction,whichisinagree-
jectories for fixed system initial state, but different en-
mentwiththelowerboundof95%imposedby(27).The
vironment estimateinitial covariance.Also inthis case,
solutionofthePAC-MPCoptimalcontrolproblem(11)
thetrajectoriesstabilizetothesetpoint.
tookinaverage22ms(andlessthan30msintheworst
case) at each control cycle when implemented in Mat-
Next,weconsiderameasurementqualitydependenton labandsolvedwithIPOPTviaCasADiona2020In-
thesystemstate.Thatis,in(17)wesubstitute(28)by
telMacBookProwith16GBRAM.Thereportedcom-
puting times were obtained without any code or solver
[De(xs,us)] =[De] (([µe] −[xs] )/(cid:96) )2,i=1,2, (29) optimization.
k k k i 0 i i i i
10

Fig. 3. PAC-MPC for double integrator with input-depen- Fig. 4. PAC-MPC for double integrator with state-depen-
dent measurements. Closed-loop state, input, and environ- dent measurements. Closed-loop state, input, and environ-
mentcovariancetrajectoriesforfixedsystemstatesanddif- mentcovariancetrajectoriesfordifferentinitialsystemstates
ferent initial environment uncertainty (gray), constraints andfixedinitialenvironmentuncertainty(gray),constraints
(dash black), true environment constraints (dash red), per- (dash black), true environment constraints (dash red), de-
ception input (dash gray), deterministic constraints (dash, terministicconstraints(dash,black).Onesimulationshown
black) . One simulation shown in blue, with corresponding in blue, with corresponding ICCs based on environment es-
ICCs based on environment estimate mean and covariance timatemeanandcovariance(solid,darkred)(solid,black).
(solid,darkred)(solid,black).
|     |     |     |     |     | [2] A. D. | Bonzanini, | A.  | Mesbah, | and S. | Di Cairano, | “On the |
| --- | --- | --- | --- | --- | --------- | ---------- | --- | ------- | ------ | ----------- | ------- |
7 Conclusions stability properties of perception-aware chance-constrained
|     |     |     |     |     | mpc | in uncertain | environments,” |     | in Proc. | 60th | IEEE Conf. |
| --- | --- | --- | --- | --- | --- | ------------ | -------------- | --- | -------- | ---- | ---------- |
DecisionandControl,2021.
| We considered | the control | of a known | system in | an un- |                                                           |     |     |     |     |     |     |
| ------------- | ----------- | ---------- | --------- | ------ | --------------------------------------------------------- | --- | --- | --- | --- | --- | --- |
|               |             |            |           |        | [3] ——,“Perception-awarechance-constrainedmodelpredictive |     |     |     |     |     |     |
knownenvironmentthatimposesconstraintsonthesys-
|                |       |                 |              |     | control | for | uncertain | environments,” |     | in Proc. | American |
| -------------- | ----- | --------------- | ------------ | --- | ------- | --- | --------- | -------------- | --- | -------- | -------- |
| tem operation. | Since | the environment | is estimated | via |         |     |           |                |     |          |          |
ControlConf.,2021.
| sensing, | the constraints | are uncertain. | As the | sensing |         |              |     |                  |     |                    |     |
| -------- | --------------- | -------------- | ------ | ------- | ------- | ------------ | --- | ---------------- | --- | ------------------ | --- |
|          |                 |                |        |         | [4] ——, | “Multi-stage |     | perception-aware |     | chance-constrained |     |
qualityisalsoaffectedbythesystemstateandhenceby
|     |     |     |     |     | MPC | with | application | to  | automated | driving,” | in Proc. |
| --- | --- | --- | --- | --- | --- | ---- | ----------- | --- | --------- | --------- | -------- |
the control actions, this results in an interdependence AmericanControlConf.,2022.
betweensensingandcontrol.Weproposedaperception-
|                          |     |       |                    |     | [5] F. Bourgault, |     | A.  | A. Makarenko, |     | S. B. | Williams, |
| ------------------------ | --- | ----- | ------------------ | --- | ----------------- | --- | --- | ------------- | --- | ----- | --------- |
| aware chance-constrained |     | model | predictive control | and |                   |     |     |               |     |       |           |
B.Grocholsky,andH.F.Durrant-Whyte,“Informationbased
astabilizingdesign,whichresultsinaconstructivepro-
|              |            |          |             |        | adaptive | robotic | exploration,” |     | IEEE | Int. Conf. | Intelligent |
| ------------ | ---------- | -------- | ----------- | ------ | -------- | ------- | ------------- | --- | ---- | ---------- | ----------- |
| cedure, when | the system | dynamics | are linear. | Future |          |         |               |     |      |            |             |
RobotsandSystems,2002.
workwillinvolveexploitingsensingmodelsconstructed [6] M.Buehler,K.Iagnemma,andS.Singh,TheDARPAurban
by machine learning that have already been tested in challenge: autonomous vehicles in city traffic. Springer,
| simulationbutposechallengestostabilityanalysis,im- |     |     |     |     | 2009,vol.56. |     |     |     |     |     |     |
| -------------------------------------------------- | --- | --- | --- | --- | ------------ | --- | --- | --- | --- | --- | --- |
proving the computational efficiency using specialized [7] M.Cognetti,M.Aggravi,C.Pacchierotti,P.Salaris,andP.R.
solvers (e.g., [12]), and evaluating the proposed control Giordano, “Perception-aware human-assisted navigation of
mobilerobotsonpersistenttrajectories,”IEEERoboticsand
strategyinapplicationsusingthecorrespondingsensing
AutomationLett.,vol.5,no.3,pp.4711–4718,2020.
models,e.g.,[27].
|     |     |     |     |     | [8] N. E. | Du Toit | and J. | W. Burdick, | “Robot | motion | planning |
| --- | --- | --- | --- | --- | --------- | ------- | ------ | ----------- | ------ | ------ | -------- |
indynamic,uncertainenvironments,”IEEETrans.Robotics,
| References        |         |               |                     |     | vol.28,no.1,pp.101–115,2011.                       |     |       |            |         |     |              |
| ----------------- | ------- | ------------- | ------------------- | --- | -------------------------------------------------- | --- | ----- | ---------- | ------- | --- | ------------ |
|                   |         |               |                     |     | [9] D.Falanga,P.Foehn,P.Lu,andD.Scaramuzza,“PAMPC: |     |       |            |         |     |              |
|                   |         |               |                     |     | Perception-aware                                   |     | model | predictive | control | for | quadrotors,” |
| [1] L. Blackmore, | M. Ono, | A. Bektassov, | and B. C. Williams, |     |                                                    |     |       |            |         |     |              |
“A probabilistic particle-control approximation of chance- inIEEEInt.Conf.IntelligentRobotsandSystems,2018.
constrained stochastic predictive control,” IEEE Trans. [10]M. Farina, L. Giulioni, L. Magni, and R. Scattolini,
Robotics,vol.26,no.3,pp.502–517,2010. “An approach to output-feedback mpc of stochastic linear
11

discrete-time systems,” Automatica, vol. 55, pp. 140–149,
2015.
[11]M. Farina, L. Giulioni, and R. Scattolini, “Stochastic linear
modelpredictivecontrolwithchanceconstraints–Areview,”
Jour.ProcessControl,vol.44,pp.53–67,2016.
[12]X. Feng, S. Di, and C. Rien, “Inexact Adjoint-based SQP
Algorithm for Real-Time Stochastic Nonlinear MPC,” in
Proc.IFACWorldCongress,2020.
[13]E. Garone, S. Di Cairano, and I. Kolmanovsky, “Reference
and command governors for systems with constraints: A
surveyontheoryandapplications,”Automatica,vol.75,pp.
306–328,2017.
[14]M.Greeff,T.D.Barfoot,andA.P.Schoellig,“Aperception-
aware flatness-based model predictive controller for fast
vision-basedmultirotorflight,”IFAC-PapersOnLine,vol.53,
no.2,pp.9412–9419,2020.
[15]K. Lee, J. Gibson, and E. A. Theodorou, “Aggressive
perception-awarenavigationusingdeepopticalflowdynamics
andPixelMPC,”IEEERoboticsandAutomationLett.,vol.5,
no.2,pp.1207–1214,2020.
[16]A. Mesbah, “Stochastic model predictive control: An
overviewandperspectivesforfutureresearch,”IEEEControl
Systems,vol.36,no.6,pp.30–44,2016.
[17]——, “Stochastic model predictive control with active
uncertainty learning: A survey on dual control,” Annual
ReviewsinControl,vol.45,pp.107–117,2018.
[18]A. Mesbah, I. V. Kolmanovsky, and S. Di Cairano,
“StochasticModelPredictiveControl,”inHandbookofModel
PredictiveControl. Springer,2019,pp.75–97.
[19]V. Murali, I. Spasojevic, W. Guerra, and S. Karaman,
“Perception-aware trajectory generation for aggressive
quadrotor flight using differential flatness,” in American
ControlConf.,2019,pp.3936–3943.
[20]B.Penin,P.R.Giordano,andF.Chaumette,“Vision-based
reactiveplanningforaggressivetargettrackingwhileavoiding
collisions and occlusions,” IEEE Robotics and Automation
Lett.,vol.3,no.4,pp.3725–3732,2018.
[21]J. A. Preiss, K. Hausman, G. S. Sukhatme, and
S. Weiss, “Simultaneous self-calibration and navigation
usingtrajectoryoptimization,”Int.Jour.RoboticsResearch,
vol.37,no.13-14,pp.1573–1594,2018.
[22]S.V.RakovicandW.S.Levine,Handbookofmodelpredictive
control. Springer,2018.
[23]J. B. Rawlings and D. Q. Mayne, Model predictive control:
Theoryanddesign. NobHillPub.,2009.
[24]P. Salaris, M. Cognetti, R. Spica, and P. R. Giordano,
“Online optimal perception-aware trajectory generation,”
IEEETrans.Robotics,vol.35,no.6,pp.1307–1322,2019.
[25]I.Spasojevic,V.Murali,andS.Karaman,“Perception-aware
timeoptimalpathparameterizationforquadrotors,”inIEEE
Int.Conf.RoboticsandAutomation,2020,pp.3213–3219.
[26]J.TordesillasandJ.P.How,“PANTHER:Perception-aware
trajectoryplannerindynamicenvironments,”IEEEAccess,
vol.10,pp.22662–22677,2022.
[27]G.Yao,P.Wang,K.Berntorp,H.Mansour,P.T.Boufounos,
andP.V.Orlik,“Extendedobjecttrackingwithautomotive
radar using B-spline chained ellipses model,” in Proc IEEE
Int. Conf. Acoustics, Speech, and Signal Proc., 2021, pp.
8408–8412.
[28]B.Zhou,J.Pan,F.Gao,andS.Shen,“Raptor:Robustand
perception-aware trajectory replanning for quadrotor fast
flight,”IEEETrans.Robotics,vol.37,no.6,pp.1992–2009,
2021.
12