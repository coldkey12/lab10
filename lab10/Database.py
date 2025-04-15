from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, LargeBinary, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from config import load_config

Base = declarative_base()

vendor_parts = Table(
    'vendor_parts', Base.metadata,
    Column('vendor_id', Integer, ForeignKey('vendors.vendor_id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True),
    Column('part_id', Integer, ForeignKey('parts.part_id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
)

class Vendor(Base):
    __tablename__ = 'vendors'
    vendor_id = Column(Integer, primary_key=True)
    vendor_name = Column(String(255), nullable=False)
    parts = relationship("Part", secondary=vendor_parts, back_populates="vendors")

class Part(Base):
    __tablename__ = 'parts'
    part_id = Column(Integer, primary_key=True)
    part_name = Column(String(255), nullable=False)
    drawing = relationship("PartDrawing", uselist=False, back_populates="part")
    vendors = relationship("Vendor", secondary=vendor_parts, back_populates="parts")

class PartDrawing(Base):
    __tablename__ = 'part_drawings'
    part_id = Column(Integer, ForeignKey('parts.part_id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    file_extension = Column(String(5), nullable=False)
    drawing_data = Column(LargeBinary, nullable=False)
    part = relationship("Part", back_populates="drawing")


def get_session():
    config = load_config()
    db_url = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['dbname']}"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session(), engine


def create_tables():
    _, engine = get_session()
    Base.metadata.create_all(engine)


def insert_vendor(name):
    session, _ = get_session()
    vendor = Vendor(vendor_name=name)
    session.add(vendor)
    session.commit()
    session.close()


def insert_many_vendors(names):
    session, _ = get_session()
    vendors = [Vendor(vendor_name=name) for name in names]
    session.add_all(vendors)
    session.commit()
    session.close()


def update_vendor(vendor_id, name):
    session, _ = get_session()
    vendor = session.query(Vendor).filter_by(vendor_id=vendor_id).first()
    if vendor:
        vendor.vendor_name = name
        session.commit()
    session.close()


def get_vendors():
    session, _ = get_session()
    vendors = session.query(Vendor).order_by(Vendor.vendor_name).all()
    for v in vendors:
        print(v.vendor_id, v.vendor_name)
    session.close()


def add_part_with_vendors(part_name, vendor_ids):
    session, _ = get_session()
    vendors = session.query(Vendor).filter(Vendor.vendor_id.in_(vendor_ids)).all()
    part = Part(part_name=part_name, vendors=vendors)
    session.add(part)
    session.commit()
    session.close()


def get_part_vendors():
    session, _ = get_session()
    results = session.query(Part.part_name, Vendor.vendor_name).join(Part.vendors).order_by(Part.part_name).all()
    for part_name, vendor_name in results:
        print(part_name, vendor_name)
    session.close()


def delete_part(part_id):
    session, _ = get_session()
    part = session.query(Part).filter_by(part_id=part_id).first()
    if part:
        session.delete(part)
        session.commit()
        print(f"Deleted part with ID: {part_id}")
    else:
        print("Part not found")
    session.close()


if __name__ == '__main__':
    create_tables()
    insert_vendor("3M Co.")
    insert_many_vendors([
        'AKM Semiconductor Inc.',
        'Asahi Glass Co Ltd.',
        'Daikin Industries Ltd.',
        'Dynacast International Inc.',
        'Foster Electric Co. Ltd.',
        'Murata Manufacturing Co. Ltd.'
    ])
    update_vendor(1, "3M Corp")
    get_vendors()
    add_part_with_vendors('SIM Tray', [1, 2])
    add_part_with_vendors('Speaker', [3, 4])
    add_part_with_vendors('Vibrator', [5, 6])
    get_part_vendors()
    delete_part(2)
