from sqlalchemy import create_engine, update, delete, select, func,Table,Column
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, Session,relationship
from sqlalchemy import String, Integer,Boolean,DateTime,Float,ForeignKey
from datetime import datetime
import random

Base=declarative_base()
engine=create_engine('sqlite:///./data/mydb.db',echo=True)
print(engine.connect())

experiment_subject = Table(
    "experiment_subject",
    Base.metadata,
    Column("experiment_id", Integer, ForeignKey("experiments.id"), primary_key=True),
    Column("subject_id", Integer, ForeignKey("subjects.id"), primary_key=True)
)
 
class Experiment(Base):
    __tablename__ = 'experiments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    type: Mapped[int] = mapped_column(Integer, nullable=False)
    finished: Mapped[bool] = mapped_column(Boolean, default=False)
    
    #relacja
    data_points: Mapped[list['DataPoint']] = relationship('DataPoint', back_populates='experiments')
    subjects: Mapped[list['Subject']] = relationship('Subject',secondary=experiment_subject,back_populates='experiments')

class DataPoint(Base):
    __tablename__ = 'datapoints'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    experiment_id: Mapped[int] = mapped_column(Integer, ForeignKey('experiments.id'), nullable=False)
    real_value: Mapped[float] = mapped_column(Float, nullable=False)
    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    
    #relacja
    experiments: Mapped['Experiment'] = relationship('Experiment', back_populates='data_points')

class Subject(Base):
    __tablename__ = 'subjects'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    gdpr_accepted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    #relacja
    experiments: Mapped[list['Experiment']] = relationship('Experiment',secondary=experiment_subject,back_populates='subjects')
    
if __name__=='__main__':
    Base.metadata.create_all(engine)
    with Session(engine) as ses:
        date_1 = datetime(2025, 10, 1, 12, 0, 0)
        date_2 = datetime(2026, 3, 15, 8, 30, 0)

        exp1 = Experiment(
            title='1 eksperyment', 
            type=1, 
            finished=True,
            created_at=date_1 
        )
        exp2 = Experiment(
            title='2 eksperyment', 
            type=2, 
            finished=False,
            created_at=date_2 
        )
        data_points_to_insert = []
        for i in range(20):
            dp = DataPoint(
                experiment_id=2 if i%2==0 else 1,
                real_value=random.random(),  
                target_value=random.random()
                )
            data_points_to_insert.append(dp)    
        ses.add_all([exp1, exp2,*data_points_to_insert])
        s1 = Subject(
           gdpr_accepted=True
        )
        ses.add_all([s1])
        experiments=ses.scalars(select(Experiment)).all()
        print('Wykonano',len(experiments),'eksperymentow')
        data_points=ses.scalars(select(DataPoint)).all()
        for dp in data_points:
            print(f'ID-{dp.id} | Real-{dp.real_value} | Target-{dp.target_value}')
        # stmt = update(Experiment).where(Experiment.finished==False).values(finished=True)
        # ses.execute(stmt)
        # ses.execute(delete(Experiment))
        # ses.execute(delete(DataPoint))
        stmt_stats=(select(Experiment.id
                        ,func.sum(DataPoint.real_value).label("total_real_sum")
                        ,func.avg(DataPoint.real_value).label("average_real_value")
                        ,func.sum(DataPoint.target_value).label("total_target_sum")
                        ,func.avg(DataPoint.target_value).label("average_target_value"))
                    .join(Experiment.data_points).group_by(Experiment.id))
        results = ses.execute(stmt_stats).all()
        for row in results:
            print(f"Eksperyment ID: {row.id} | Suma (real): {row.total_real_sum:.2f} | Średnia(real): {row.average_real_value:.2f}  | Suma (target): {row.total_target_sum:.2f} | Średnia (target): {row.average_target_value:.2f}")
        ses.flush()
        ses.commit()