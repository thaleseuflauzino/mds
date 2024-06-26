import Header from '../../components/header'
import membros from '../../mocks/members'
import CardMember from './card-member'

import styles from './style.module.css'

export default function AboutUs(){

    return (
        <div>
            <Header/>
            <div className={styles.aboutUsContext}>
                <h2 className={styles.aboutUsTitle}>Sobre nós</h2>
                <p className={styles.aboutUsP}>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Ullam dignissimos maxime eveniet odio unde nostrum temporibus incidunt esse quaerat sit delectus ut, quis soluta assumenda exercitationem? Molestias velit quas delectus?</p>
                <img className={styles.aboutUsImg} src='../../assets/download.jpg' alt='Foto de toda a equipe'/>
                <h2 className={styles.aboutUsTitle}>Agora, um pouco de cada um</h2>
                {membros.map(membro => <CardMember key={membro.id} nome={membro.nome} descricao={membro.descricao} github={membro.github} id={membro.id}/>)}
            </div>
        
        </div>
    )
}